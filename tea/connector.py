import asyncio


class Connector:
    name = None
    _enable_connector = True

    def __init__(self, tea):
        self.setting = {}
        self.tea = tea
        self.dispatch = self.tea.dispatch

    def run(self):
        pass

    async def stop(self):
        pass
