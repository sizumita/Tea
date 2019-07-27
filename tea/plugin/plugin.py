from collections import OrderedDict
from . import decorator
from . import config
import os


class Plugin:
    name = None
    event = decorator.event
    events = {}
    setting = {}

    def __init__(self, _tea, path='config.yml'):
        self.tea = _tea
        self.dispatch = self.tea.dispatch
        self.config = config.ConfigLoader(os.path.join(os.getcwd(), self.tea.path, self.name, path))

    def add_event(self, event):
        name = event.name
        priority = event.priority
        if not name in self.events.keys():
            self.events[name] = OrderedDict(LOWEST=[], LOW=[], NORMAL=[], HIGH=[], HIGHEST=[], MONITOR=[])
        self.events[name][priority].append(event)

