import yaml

import os


class ConfigLoader:
    def __init__(self, path):
        try:
            with open(shaping_path(path), 'r') as f:
                self.data = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            raise

    def get(self, k, default):
        if k in self.data.keys():
            return self.data[k]
        return default


def shaping_path(path):
    if path.endswith(".py"):
        return os.path.dirname(path) + "/config.yml"
    elif path.endswith("/config.yml"):
        return path
    else:
        return os.path.join(path, "config.yml")
