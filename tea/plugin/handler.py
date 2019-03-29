import asyncio


class EventHandler:
    def __init__(self, name, callback, **kwargs):
        self.name = name
        self.callback = callback
        self.wait = kwargs.get('wait', 0)
        self.connector = kwargs.get('connector', None)

    async def do(self, *args, **kwargs):
        if self.wait:
            await asyncio.sleep(self.wait)
        result = await self.callback(*args, **kwargs)
        return result
