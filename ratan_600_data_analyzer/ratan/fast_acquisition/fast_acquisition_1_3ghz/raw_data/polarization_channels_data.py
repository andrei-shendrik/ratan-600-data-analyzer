import copy
from dataclasses import dataclass

import numpy as np


@dataclass
class PolarizationChannelsData:

    """
            c0 1-2 GHz
            c1 2-3 GHz
    """
    _c0p0_data: np.ndarray
    _c0p1_data: np.ndarray
    _c1p0_data: np.ndarray
    _c1p1_data: np.ndarray

    @property
    def c0p0_data(self):
        return self._c0p0_data

    @c0p0_data.setter
    def c0p0_data(self, value):
        self._c0p0_data = copy.deepcopy(value)

    @property
    def c0p1_data(self):
        return self._c0p1_data

    @c0p1_data.setter
    def c0p1_data(self, value):
        self._c0p1_data = copy.deepcopy(value)

    @property
    def c1p0_data(self):
        return self._c1p0_data

    @c1p0_data.setter
    def c1p0_data(self, value):
        self._c1p0_data = copy.deepcopy(value)

    @property
    def c1p1_data(self):
        return self._c1p1_data

    @c1p1_data.setter
    def c1p1_data(self, value):
        self._c1p1_data = copy.deepcopy(value)