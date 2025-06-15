from abc import ABC, abstractmethod
from pathlib import Path

from ratan_600_data_analyzer.ratan.ratan_observation_calibrator import RatanObservationCalibrator
from ratan_600_data_analyzer.ratan.ratan_observation_reader import RatanObservationReader


class RatanObservationFactory(ABC):

    @abstractmethod
    def create_reader(self, file: Path) -> RatanObservationReader:
        pass

    @abstractmethod
    def create_calibrator(self) -> RatanObservationCalibrator:
        pass