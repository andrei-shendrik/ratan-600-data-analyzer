import copy

import numpy as np

from ratan_600_data_analyzer.ratan.data_layout import DataLayout
from ratan_600_data_analyzer.ratan.ratan_observation_data import RatanObservationData


class SSPCData(RatanObservationData):

    def __init__(self, array_3d: np.ndarray):
        self._array_3d = copy.deepcopy(array_3d)

    @property
    def array_3d(self):
        return self._array_3d

    @array_3d.setter
    def array_3d(self, array_3d):
        self._array_3d = array_3d