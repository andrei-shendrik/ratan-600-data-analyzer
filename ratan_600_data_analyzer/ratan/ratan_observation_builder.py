from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeGuard

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

# class RatanObservationBuilder:
#     def __init__(self, file: Path):
#         self._file = file
#         self._observation = None
#
#     def read(self) -> RatanObservationBuilder:
#         reader = RatanReaderFactory.create_reader(self._file)
#         self._observation = reader.read(self._file)
#         return self
#
#     # todo
#     # def calibrate(self, method: str) -> RatanObservationBuilder:
#     #     calibrator = RatanCalibratorFactory.create_calibrator(method, self._observation)
#     #     calibrator.calibrate(self._observation)
#     #     return self
#
#     def write(self, file_type: str, output_file: Path) -> RatanObservationBuilder:
#         writer = RatanWriterFactory.create_writer(self._observation, file_type)
#         writer.write(output_file)
#         return self
#
#     def build(self) -> RatanObservation:
#         return self._observation