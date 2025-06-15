from __future__ import annotations
from pathlib import Path

from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation
from ratan_600_data_analyzer.ratan.ratan_reader_factory import RatanReaderFactory


class RatanObservationBuilder:
    def __init__(self, file: Path):
        self._file = file
        self._observation = None

    def read(self) -> RatanObservationBuilder:
        reader = RatanReaderFactory.create_reader(self._file)
        self._observation = reader.read(self._file)
        return self

    # def calibrate(self, method: str) -> RatanObservationBuilder:
    #     calibrator = RatanCalibratorFactory.create_calibrator(method, self._observation)
    #     calibrator.calibrate(self._observation)
    #     return self

    def write(self, file: Path, file_type: str) -> RatanObservationBuilder:
        #todo
        return self

    def build(self) -> RatanObservation:
        return self._observation