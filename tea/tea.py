import asyncio
import sys
import traceback
from collections import OrderedDict
from .handlers import TeaHandler, CancelHandler
from .plugin.manager import PluginManager
from .plugin.plugin import Plugin


class Tea:
    _listeners = {}
    _events = {}
    candidacy_connectors = {}
    connectors = {}

    def __init__(self, plugin_filepath="plugins", loop=None):
        self.loop = loop if loop else asyncio.get_event_loop()
        self.manager = PluginManager(self, plugin_filepath)
        self.manager.register_plugins()
        self._ready = asyncio.Event(loop=self.loop)

    def register_events(self, events):
        for event in events:
            coro: Plugin = event[0]
            priority = event[1]
            name = coro.__name__
            if name.startswith("on_"):
                name = name[3:]
            if not name in self._events.keys():
                self._events[name] = OrderedDict(LOWEST=[], LOW=[], NORMAL=[], HIGH=[], HIGHEST=[], MONITOR=[])
            self._events[name][priority].append(coro)

    def dispatch(self, event, *args, **kwargs):

        listeners = self._listeners.get(event)
        if listeners:
            removed = []
            for i, (future, condition) in enumerate(listeners):
                if future.cancelled():
                    removed.append(i)
                    continue
                try:
                    result = condition(*args)
                except Exception as exc:
                    future.set_exception(exc)
                    removed.append(i)
                else:
                    if result:
                        if len(args) == 0:
                            future.set_result(None)
                        elif len(args) == 1:
                            future.set_result(args[0])
                        else:
                            future.set_result(args)
                        removed.append(i)

            if len(removed) == len(listeners):
                self._listeners.pop(event)
            else:
                for idx in reversed(removed):
                    del listeners[idx]

        try:
            coro_list = self._events.get(event)
        except KeyError:
            pass
        else:
            asyncio.ensure_future(self._run_event(coro_list, event, *args, **kwargs), loop=self.loop)

    async def _run_event(self, coros, event_name, *args, **kwargs):
        try:
            if not coros:
                return
            for priority, events in coros.items():
                result = None
                for coro in events:
                    result = await coro(*args, **kwargs)
                    if isinstance(result, TeaHandler):
                        self.dispatch(result.event[0], result.event[1])
                    if isinstance(result, CancelHandler):
                        break
                if isinstance(result, CancelHandler):
                    break
        except asyncio.CancelledError:
            pass
        except Exception:
            try:
                await self.on_error(event_name, *args, **kwargs)
            except asyncio.CancelledError:
                pass

    def wait_for(self, event, *, check=None, timeout=None):
        future = self.loop.create_future()
        if check is None:
            def _check(*args):
                return True

            check = _check

        ev = event.lower()
        try:
            listeners = self._listeners[ev]
        except KeyError:
            listeners = []
            self._listeners[ev] = listeners

        listeners.append((future, check))
        return asyncio.wait_for(future, timeout, loop=self.loop)

    async def on_error(self, event_method, *args, **kwargs):
        print('Ignoring exception in {}'.format(event_method), file=sys.stderr)
        traceback.print_exc()

    def register_connector(self, name):
        if name in self.candidacy_connectors:
            self.candidacy_connectors[name].setup(self)
            self.connectors[name] = self.candidacy_connectors[name]
            return True
        else:
            return None

    def blend(self):
        try:
            for key, value in self.connectors.items():
                value.run()
            self.loop.run_forever()
        except KeyboardInterrupt:
            _cleanup_loop(self.loop)
            self.loop.stop()
            self.loop.close()


def _cleanup_loop(loop):
    try:
        task_retriever = asyncio.Task.all_tasks
    except AttributeError:
        # future proofing for 3.9 I guess
        task_retriever = asyncio.all_tasks

    all_tasks = {t for t in task_retriever(loop=loop) if not t.done()}
    _cancel_tasks(loop, all_tasks)
    if sys.version_info >= (3, 6):
        loop.run_until_complete(loop.shutdown_asyncgens())


def _cancel_tasks(loop, tasks):
    if not tasks:
        return

    gathered = asyncio.gather(*tasks, loop=loop, return_exceptions=True)
    gathered.cancel()

    def stop_and_silence(fut):
        loop.stop()
        try:
            fut.result()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            loop.call_exception_handler({
                'message': 'Unhandled exception during Client.run shutdown.',
                'exception': e,
                'future': fut
            })

    gathered.add_done_callback(stop_and_silence)
    while not gathered.done():
        loop.run_forever()

    for task in tasks:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler({
                'message': 'Unhandled exception during Client.run shutdown.',
                'exception': task.exception(),
                'task': task
            })
