from pydataconfig.base_loader import ConfigLoader


class CompositeLoader(ConfigLoader):

    def __init__(self, config_loaders: list[ConfigLoader]):
        self.config_loaders = config_loaders

    def load(self, config):
        for config_loader in self.config_loaders:
            config_loader.load(config)
