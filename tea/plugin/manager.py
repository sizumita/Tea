import os
import yaml
from importlib import import_module


class PluginManager:
    def __init__(self, _tea, path="plugins"):
        self.path = path
        self.plugins = {}
        self.tea = _tea
        self.connectors = {}

    def register_plugins(self):
        for path in os.listdir(self.path):
            if path == "__pycache__":
                continue
            if os.path.isdir(os.path.join(self.path, path)):
                config_path = os.path.join(os.getcwd(), self.path, path, "config.yml")
                with open(config_path) as f:
                    data = yaml.load(f, yaml.FullLoader)
                try:
                    if data['is_connector']:
                        file = data['setup'].replace(".py", "")
                        name = data['name']
                        module_name = f"{self.path}.{path}.{file}"
                        module = import_module(module_name)
                        connector = module.get_connector()
                        connector.setting = data
                        self.tea.candidacy_connectors[name] = connector
                        continue
                except KeyError:
                    pass
                file = data['setup'].replace(".py", "")
                name = data['name']
                module_name = f"{self.path}.{path}.{file}"
                module = import_module(module_name)
                plugin = module.setup()
                events = plugin.setup(self.tea, data)
                plugin.name = name
                self.tea.register_events(events)
                self.plugins[name] = plugin

    def get_plugin(self, name):
        if name in self.plugins.keys():
            return self.plugins[name]
        return None



