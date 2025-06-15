from abc import ABC, abstractmethod
from pathlib import Path

from ratan_600_data_analyzer.observation.observation import Observation


class ObservationReader(ABC):

    @abstractmethod
    def can_read(self, file_path: Path) -> Observation:
        pass

    @abstractmethod
    def read(self, file_path: Path) -> Observation:
        pass

    @abstractmethod
    def read_metadata(self, file_path: Path) -> Observation:
        pass
