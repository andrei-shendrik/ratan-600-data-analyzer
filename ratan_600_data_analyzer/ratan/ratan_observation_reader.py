from abc import ABC, abstractmethod
from pathlib import Path

from ratan_600_data_analyzer.observation.observation_reader import ObservationReader
from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation


class RatanObservationReader(ObservationReader, ABC):

    @abstractmethod
    def can_read(self, file: Path) -> bool:
        pass

    @abstractmethod
    def read(self, file: Path) -> RatanObservation:
        pass

    @abstractmethod
    def read_metadata(self, file: Path) -> RatanObservation:
        pass