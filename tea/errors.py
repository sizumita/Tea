class TeaError(Exception):
    pass


class PluginFileNotFoundError(TeaError):
    pass


class PluginLoadError(TeaError):
    pass
