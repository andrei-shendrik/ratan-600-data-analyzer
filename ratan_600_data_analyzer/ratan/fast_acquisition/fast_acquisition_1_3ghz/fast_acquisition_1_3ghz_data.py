import copy

from ratan_600_data_analyzer.ratan.ratan_observation_data import RatanObservationData


class FastAcquisition1To3GHzData(RatanObservationData):
    def __init__(self, array_3d):
        # todo
        self._pol_channels_data = None
        self._kurtosis_data = None
        self._array_3d = copy.deepcopy(array_3d)

    @property
    def array_3d(self):
        return self._array_3d

    @array_3d.setter
    def array_3d(self, array_3d):
        self._array_3d = array_3d

