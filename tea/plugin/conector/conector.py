import asyncio
from tea import tea as t


class Connector:
    def __init__(self, **options):
        self.run_func = None
        self.run_func_params = None
        self.events = []
        self.tea = None
        self.loop = asyncio.get_event_loop()

    def set_tea(self, tea: t.Tea):
        self.tea = tea

    async def event(self, name, *args, **kwargs):
        await self.tea.event(name, connector=True, *args, **kwargs)

    def set_running(self, func, *args):
        self.run_func = func
        self.run_func_params = args

    def run(self):
        self.run_func(*self.run_func_params)
