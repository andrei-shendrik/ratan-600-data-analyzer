from abc import ABC, abstractmethod
from pathlib import Path

from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation
from ratan_600_data_analyzer.ratan.ratan_observation_builder import RatanObservationBuilder
from ratan_600_data_analyzer.ratan.ratan_observation_calibrator import RatanObservationCalibrator
from ratan_600_data_analyzer.ratan.ratan_observation_reader import RatanObservationReader
from ratan_600_data_analyzer.ratan.ratan_observation_writer import RatanObservationWriter


class RatanObservationFactory(ABC):

    @abstractmethod
    def create_reader(self, file: Path) -> RatanObservationReader:
        pass

    @abstractmethod
    def create_calibrator(self) -> RatanObservationCalibrator:
        pass

    @abstractmethod
    def create_writer(self, observation: RatanObservation, file_type: str) -> RatanObservationWriter:
        pass

    @abstractmethod
    def create_builder(self, file: Path) -> RatanObservationBuilder:
        pass
