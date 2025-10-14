import copy

import numpy as np
from ratan_600_data_analyzer.ratan.ratan_observation_data import RatanObservationData


class FastAcquisition1To3GHzData(RatanObservationData):

    def __init__(self, channel_mapping: dict):
        super().__init__()
        self._channel_mapping = channel_mapping
        self._lhcp = None
        self._rhcp = None
        self._stokes_i = None
        self._stokes_v = None

    @property
    def lhcp(self):
        return self._lhcp

    @lhcp.setter
    def lhcp(self, array: np.ndarray):
        self._lhcp = copy.deepcopy(array)

    @property
    def rhcp(self):
        return self._rhcp

    @rhcp.setter
    def rhcp(self, array: np.ndarray):
        self._rhcp = copy.deepcopy(array)

    @property
    def stokes_i(self):
        return self._stokes_i

    @stokes_i.setter
    def stokes_i(self, array: np.ndarray):
        self._stokes_i = copy.deepcopy(array)

    @property
    def stokes_v(self):
        return self._stokes_v

    @stokes_v.setter
    def stokes_v(self, array: np.ndarray):
        self._stokes_v = copy.deepcopy(array)

    @property
    def pol_channel0(self):
        target_attr = self._channel_mapping['pol_channel0']
        return getattr(self, target_attr)

    @pol_channel0.setter
    def pol_channel0(self, array: np.ndarray):
        target_attr = self._channel_mapping['pol_channel0']
        setattr(self, target_attr, array)

    @property
    def pol_channel1(self):
        target_attr = self._channel_mapping['pol_channel1']
        return getattr(self, target_attr)

    @pol_channel1.setter
    def pol_channel1(self, array: np.ndarray):
        target_attr = self._channel_mapping['pol_channel1']
        setattr(self, target_attr, array)