from .plugin import config
import os


class Connector:
    name = None
    _enable_connector = True

    def __init__(self, tea):
        self.setting = {}
        self.tea = tea
        self.dispatch = self.tea.dispatch
        self.config = config.ConfigLoader(os.path.join(os.getcwd(), self.tea.path, self.name, 'config.yml'))

    def run(self):
        pass

    async def stop(self):
        pass
