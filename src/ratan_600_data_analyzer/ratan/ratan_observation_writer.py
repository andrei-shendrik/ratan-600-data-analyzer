from abc import ABC, abstractmethod
from pathlib import Path

from ratan_600_data_analyzer.ratan.data_receiver import DataReceiver
from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation


class RatanObservationWriter(ABC):

    def __init__(self, observation: RatanObservation):
        self._observation = observation

    @abstractmethod
    def write(self, output_file: Path):
        pass

    @staticmethod
    @abstractmethod
    def supports(data_receiver: DataReceiver, file_type: str) -> bool:
        pass

    @property
    @abstractmethod
    def observation(self):
        pass