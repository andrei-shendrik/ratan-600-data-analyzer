import copy

import numpy as np


class CoordinateAxes:
    def __init__(self):
        self._frequency_axis = None
        self._time_axis = None
        self._arcsec_axis = None

    @property
    def frequency_axis(self):
        return copy.deepcopy(self._frequency_axis)

    @frequency_axis.setter
    def frequency_axis(self, array: np.ndarray):
        self._frequency_axis = copy.deepcopy(array)

    @property
    def time_axis(self):
        return copy.deepcopy(self._time_axis)

    @time_axis.setter
    def time_axis(self, array: np.ndarray):
        self._time_axis = copy.deepcopy(array)

    @property
    def arcsec_axis(self):
        return copy.deepcopy(self._arcsec_axis)

    @arcsec_axis.setter
    def arcsec_axis(self, array: np.ndarray):
        self._arcsec_axis = copy.deepcopy(array)

