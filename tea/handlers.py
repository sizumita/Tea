class TeaHandler:
    event = None

    def __init__(self, **options):
        for key, value in options.items():
            setattr(self, key, value)


class CancelHandler(TeaHandler):
    def __init__(self, **options):
        super().__init__(**options)
        self.event = ("event_canceled", self)

