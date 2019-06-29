from collections import OrderedDict
from . import decorator


class Plugin:
    name = None
    event = decorator.event
    events = {}
    setting = {}

    def __init__(self, tea):
        self.tea = tea

    def add_event(self, event):
        name = event.name
        priority = event.priority
        if not name in self.events.keys():
            self.events[name] = OrderedDict(LOWEST=[], LOW=[], NORMAL=[], HIGH=[], HIGHEST=[], MONITOR=[])
        self.events[name][priority].append(event)

