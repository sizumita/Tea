import asyncio
import sys
import traceback
import uuid
from collections import OrderedDict
from .plugin.plugin import Plugin
from .context import Context
import importlib
from . import errors


class Tea:
    _listeners = {}
    _events = {}
    connectors = {}
    raise_events = {}
    plugins = {}

    def __init__(self, path='plugins', loop=None):
        self.loop = loop if loop else asyncio.get_event_loop()
        self._ready = asyncio.Event(loop=self.loop)
        self.path = path

    @property
    def events(self):
        return self._events

    def add_event(self, func):
        name = func.name
        priority = func.priority
        if name.startswith("on_"):
            name = name[3:]
        if not name in self._events.keys():
            self._events[name] = OrderedDict(LOWEST=[], LOW=[], NORMAL=[], HIGH=[], HIGHEST=[], MONITOR=[])
        self._events[name][priority].append(func)

    def _load_from_class_spec(self, cls):
        cls = cls(self)
        self.plugins[cls.name] = cls
        for name in dir(cls):
            func = getattr(cls, name, None)
            if callable(func):
                is_allow_command = getattr(func, '__allow_command__', None)
                if not is_allow_command:
                    continue

                self.add_event(func)

    def get_plugin(self, name):
        if name in self.plugins.keys():
            return self.plugins.get(name)

        return None

    def load_plugin(self, name):
        try:
            lib = importlib.import_module(f'{self.path}.{name}.main')
        except ImportError as e:
            raise errors.PluginNotFound(name, e) from e
        else:
            for key, value in lib.__dict__.items():
                if callable(value):
                    is_enable = getattr(value, '__enable', None)
                    if is_enable:
                        if not isinstance(value(self), Plugin):
                            raise errors.PluginCannotLoad(name)
                        self._load_from_class_spec(value)

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
                            future.set_result()
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
            coro_list = self._events[event]
        except KeyError:
            pass
        else:
            asyncio.ensure_future(self._run_event(coro_list, event, *args, **kwargs), loop=self.loop)

    async def _run_event(self, coros, event_name, *args, **kwargs):
        try:
            if not coros:
                return
            for priority, events in coros.items():
                event = asyncio.Event()
                event_id = str(uuid.uuid4())
                self.raise_events[event_id] = event
                connector = kwargs.pop('connector', None)
                context = Context(self, event_id, event_name, connector=connector)
                pass_context = kwargs.pop('pass_context', True)

                for coro in events:
                    if pass_context:
                        await coro(context, *args, **kwargs)
                    else:
                        await coro(*args, **kwargs)
                    if context.is_finish():
                        del self.raise_events[event_id]

                del self.raise_events[event_id]
                self.dispatch('finish_event', event_name, True)

        except asyncio.CancelledError:
            pass
        except Exception:
            try:
                await self.on_error(event_name, *args, **kwargs)
                self.dispatch('finish_event', event_name, False)
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
        self.dispatch('error', event_method, *args, **kwargs)
        print('Ignoring exception in {}'.format(event_method), file=sys.stderr)
        traceback.print_exc()

    def load_connector(self, name):
        try:
            lib = importlib.import_module(f'{self.path}.{name}.main')
        except ImportError as e:
            raise errors.PluginNotFound(f'{self.path}.{name}.main', e) from e
        else:
            for name in dir(lib):
                value = getattr(lib, name, None)

                if getattr(value, '_enable_connector', False):
                    value = value(self)
                    self.connectors[value.name] = value

    def get_connector(self, name):
        if name in self.connectors.keys():
            return self.connectors[name]

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
