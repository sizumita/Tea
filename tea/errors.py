class TeaError(Exception):
    pass


class TeaException(TeaError):
    pass


class PluginFileNotFoundError(TeaError):
    pass


class PluginLoadError(TeaError):
    pass
