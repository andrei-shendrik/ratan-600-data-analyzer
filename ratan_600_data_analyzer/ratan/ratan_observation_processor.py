from abc import ABC, abstractmethod
from pathlib import Path

from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation


class RatanObservationProcessor(ABC):
    def __init__(self, file: Path) -> RatanObservation:
        return None

    @abstractmethod
    def process(self, file: Path) -> RatanObservation:
        pass