import copy

from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_data import \
    FastAcquisition1To3GHzData
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_metadata import \
    FastAcquisition1To3GHzMetadata
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.raw_data.fast_acquisition_1_3ghz_raw_data import \
    FastAcquisition1To3GHzRawData
from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation


class FastAcquisition1To3GHzObservation(RatanObservation):

    def __init__(self, metadata: FastAcquisition1To3GHzMetadata, data: FastAcquisition1To3GHzData,
                 raw_data: FastAcquisition1To3GHzRawData = None):
        super().__init__(metadata, data)
        self._metadata = copy.deepcopy(metadata)
        self._data = copy.deepcopy(data)
        self._raw_data = copy.deepcopy(raw_data)

    @property
    def metadata(self) -> FastAcquisition1To3GHzMetadata:
        return self._metadata

    @metadata.setter
    def metadata(self, metadata: FastAcquisition1To3GHzMetadata):
        self._metadata = copy.deepcopy(metadata)

    @property
    def data(self) -> FastAcquisition1To3GHzData:
        return self._data

    @data.setter
    def data(self, data: FastAcquisition1To3GHzData):
        self._data = copy.deepcopy(data)

    @property
    def raw_data(self) -> FastAcquisition1To3GHzRawData:
        return self._raw_data

    @raw_data.setter
    def raw_data(self, raw_data: FastAcquisition1To3GHzRawData):
        self._raw_data = copy.deepcopy(raw_data)