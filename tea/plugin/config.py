import yaml


class ConfigLoader:
    def __init__(self, path='config.yml'):
        self.path = path
        with open(self.path, mode='r') as f:
            self.data = yaml.load(f, yaml.FullLoader)

    def get(self, i, d=None):
        if i in self.data.keys():
            return self.data[i]
        return d

    @property
    def keys(self):
        return self.data.keys()

    @property
    def values(self):
        return self.data.values()

    @property
    def items(self):
        return self.data.items()
