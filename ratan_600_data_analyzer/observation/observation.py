from abc import ABC, abstractmethod


class Observation(ABC):

    def __init__(self, metadata, data):
        self._metadata = metadata
        self._data = data

    @property
    @abstractmethod
    def metadata(self):
        pass

    @property
    @abstractmethod
    def data(self):
        pass