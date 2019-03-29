class Event:
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.connector_event = kwargs.get('connector', False)
        self.kwargs = kwargs
