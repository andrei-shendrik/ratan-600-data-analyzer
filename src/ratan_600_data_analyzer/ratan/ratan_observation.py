from abc import abstractmethod, ABC

from ratan_600_data_analyzer.observation.observation import Observation
from ratan_600_data_analyzer.ratan.ratan_observation_data import RatanObservationData


class RatanObservation(Observation, ABC):
    def __init__(self, metadata, data: RatanObservationData):
        super().__init__(metadata, data)

    @property
    @abstractmethod
    def metadata(self):
        pass

    @property
    @abstractmethod
    def data(self) -> RatanObservationData:
        pass