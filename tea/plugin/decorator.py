import asyncio
from tea.errors import TeaException
from tea.priority import *


def event(name=None, *args, **kwargs):

    def decorator(coro):
        if not asyncio.iscoroutinefunction(coro):
            raise TeaException('event registered must be a coroutine function')

        coro.name = name or coro.__name__
        coro.__allow_command__ = True
        coro.priority = NORMAL

        for key, value in kwargs.items():
            setattr(coro, key, value)

        return coro

    return decorator


def enable_plugin(name=None, *args, **kwargs):

    def decorator(cls):
        cls.__enable = True
        cls.name = name or cls.__name__

        for key, value in kwargs.items():
            setattr(cls, key, value)

        return cls

    return decorator
