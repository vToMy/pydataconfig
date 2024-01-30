import abc


class ConfigLoader(abc.ABC):

    @abc.abstractmethod
    def load(self, config):
        pass
