import os
from .errors import PluginFileNotFoundError, PluginLoadError
import glob
from importlib import import_module
from tea.config import ConfigLoader


def delete_slash(fp) -> str:
    if fp.startswith("/"):
        fp = fp[1:]
    if fp.endswith("/"):
        fp = fp[:-1]
    return fp


class Tea:
    def __init__(self, plugin_filename="plugins"):
        self.db = None
        self.plugin_path = plugin_filename
        self.plugins = {}
        self.connector = None

        if not os.path.isdir(os.path.join(os.getcwd(), self.plugin_path)):
            raise PluginFileNotFoundError('Plugin Directory not found')

        self.plugin_paths = {os.path.basename(os.path.dirname(x)): x for x in glob.glob(os.path.join(os.getcwd(),
                                                                                                     self.plugin_path,
                                                                                                     "*/"))}

        for name in list(self.plugin_paths):
            path = self.plugin_paths[name]
            if name.startswith("__") and name.endswith("__"):
                del self.plugin_paths[name]
                continue
            loader = ConfigLoader(path)
            _module = import_module("{0}.{1}.{2}".format(delete_slash(self.plugin_path), name,
                                                         loader.get('plugin_file', name.lower()).replace(".py", "")))

            try:
                r = _module.get_connector(self)
                self.connector = r
                continue
            except AttributeError:
                pass

            try:
                r = _module.get_plugin(self)
                self.plugins[name] = r
                continue
            except AttributeError:
                raise PluginLoadError("Plugin Loader is not found")

    def run(self):
        self.connector.run()

    async def event(self, event, *args, **kwargs):
        for plugin in self.plugins.values():
            await plugin.event(event, *args, **kwargs)
