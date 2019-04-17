import asyncio
from tea.errors import TeaException
from tea.priority import *


class Plugin:
    name = None

    def __init__(self):
        self.tea = None
        self.events = []

    def setup(self, tea):
        self.tea = tea
        return self.events

    def event(self, priority=NORMAL):

        def decorator(coro):
            if not asyncio.iscoroutinefunction(coro):
                raise TeaException('event registered must be a coroutine function')
            self.events.append((coro, priority))
            return coro
        return decorator

