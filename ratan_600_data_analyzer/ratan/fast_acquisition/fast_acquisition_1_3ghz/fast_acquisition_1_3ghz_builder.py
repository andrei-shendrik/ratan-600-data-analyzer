from __future__ import annotations
from pathlib import Path

from ratan_600_data_analyzer.ratan.data_receiver import DataReceiver
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import \
    FastAcquisition1To3GHzObservation
from ratan_600_data_analyzer.ratan.ratan_observation_builder import RatanObservationBuilder
from ratan_600_data_analyzer.ratan.ratan_reader_factory import RatanReaderFactory


class FastAcquisition1To3GHzBuilder(RatanObservationBuilder):
    def __init__(self, file: Path):
        super().__init__(file)

    @property
    def receiver(self) -> DataReceiver:
        return self._receiver

    @receiver.setter
    def receiver(self, value):
        self._receiver = value

    def build(self) -> FastAcquisition1To3GHzObservation:
        return FastAcquisition1To3GHzObservation(self._metadata, self._data)

    def read(self) -> FastAcquisition1To3GHzBuilder:
        reader = RatanReaderFactory.create_reader(self._file)
        observation = reader.read(self._file)

        self._metadata = observation.metadata
        self._data = observation.data
        return self

    def remove_spikes(self) -> FastAcquisition1To3GHzBuilder:
        return self

    def time_downsample(self, factor: int) -> FastAcquisition1To3GHzBuilder:
        return self