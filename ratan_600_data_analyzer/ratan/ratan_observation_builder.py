from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ratan_600_data_analyzer.ratan.data_receiver import DataReceiver
from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation


class RatanObservationBuilder(ABC):
    def __init__(self, file: Path):
        self._file = file
        self._receiver = None
        self._data = None
        self._metadata = None

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def build(self) -> RatanObservation:
        pass

    @property
    @abstractmethod
    def receiver(self) -> DataReceiver:
        pass

    @receiver.setter
    @abstractmethod
    def receiver(self, value):
        pass