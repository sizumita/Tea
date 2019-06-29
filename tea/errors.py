class TeaError(Exception):
    pass


class PluginError(Exception):
    def __init__(self, message=None, *args, name):
        self.name = name
        message = message or 'Extension {!r} had an error.'.format(name)
        # clean-up @everyone and @here mentions
        m = message.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
        super().__init__(m, *args)


class TeaException(TeaError):
    pass


class PluginNotFound(PluginError):
    def __init__(self, name, original):
        self.original = original
        fmt = 'Plugin {0!r} could not be loaded.'
        super().__init__(fmt.format(name), name=name)


class PluginCannotLoad(PluginError):
    def __init__(self, name):
        fmt = 'Plugin {0!r} is not class tea.Plugin.'
        super().__init__(fmt.format(name), name=name)
