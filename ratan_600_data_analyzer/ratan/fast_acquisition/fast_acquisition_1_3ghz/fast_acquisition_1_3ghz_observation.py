from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation


class FastAcquisition1To3GHzObservation(RatanObservation):

    def __init__(self, fast_acquisition_metadata, data):
        super().__init__(fast_acquisition_metadata, data)

    @property
    def metadata(self):
        return self._metadata

    @property
    def data(self):
        return self._data