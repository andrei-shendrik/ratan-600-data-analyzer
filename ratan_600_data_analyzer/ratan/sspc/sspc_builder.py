from __future__ import annotations
from pathlib import Path

from ratan_600_data_analyzer.ratan.data_receiver import DataReceiver
from ratan_600_data_analyzer.ratan.ratan_observation_builder import RatanObservationBuilder
from ratan_600_data_analyzer.ratan.ratan_reader_factory import RatanReaderFactory
from ratan_600_data_analyzer.ratan.sspc.sspc_observation import SSPCObservation


class SSPCBuilder(RatanObservationBuilder):
    def __init__(self, file: Path):
        super().__init__(file)

    def read(self) -> SSPCBuilder:
        reader = RatanReaderFactory.create_reader(self._file)
        observation = reader.read(self._file)

        self._metadata = observation.metadata
        self._data = observation.data
        return self

    def build(self) -> SSPCObservation:
        return SSPCObservation(self._metadata, self._data)

    @property
    def receiver(self) -> DataReceiver:
        return self._receiver

    @receiver.setter
    def receiver(self, value):
        self._receiver = value