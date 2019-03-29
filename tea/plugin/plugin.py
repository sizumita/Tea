from .handler import EventHandler


class Plugin:
    def __init__(self):
        self.handlers = []
        self.tea = None

    def set_tea(self, tea):
        self.tea = tea

    def event(self, *args, **kwargs):
        def decorator(func):
            result = create_event_handler(*args, **kwargs)(func)
            self.add_event(result)
            return result

        return decorator

    def add_event(self, handler: EventHandler):
        self.handlers.append(handler)

    async def connector_event(self, event, *args, **kwargs):
        connector = kwargs.get('connector', None)
        for handler in self.handlers:
            if handler.name == event and connector == handler.connector:
                result = await handler.do(*args, **kwargs)
                print(result)


def create_event_handler(name=None, **attrs):

    def decorator(func):
        event_name = name or func.__name__
        return EventHandler(event_name, func, **attrs)
    return decorator

