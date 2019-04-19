import asyncio
from .tea import Tea


class Connector:
    tea = None

    def __init__(self):
        self.enable = True
        self.setting = {}

    def setup(self, tea: Tea):
        self.tea = tea

    def send_event(self, event, *args, **kwargs):
        self.tea.dispatch(event, *args, **kwargs)

    def run(self):
        return True
