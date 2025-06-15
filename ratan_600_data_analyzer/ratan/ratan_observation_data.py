from abc import abstractmethod

from ratan_600_data_analyzer.observation.observation_data import ObservationData


class RatanObservationData(ObservationData):

    @property
    @abstractmethod
    def array_3d(self):
        pass

    @array_3d.setter
    @abstractmethod
    def array_3d(self, array_3d):
        pass