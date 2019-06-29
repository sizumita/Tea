class Context:
    def __init__(self, tea, event_id, event_name: str, *args, **kwargs):
        self.tea = tea
        self.args = args
        self.id = event_id
        self.name = event_name

        for key, value in kwargs.items():
            setattr(self, key, value)

    def is_finish(self):
        return self.tea.raise_events[self.id].is_set()

    async def finish(self):
        return await self.finish()

    async def cancel(self):
        """finish the event"""
        self.tea.raise_events[self.id].set()



