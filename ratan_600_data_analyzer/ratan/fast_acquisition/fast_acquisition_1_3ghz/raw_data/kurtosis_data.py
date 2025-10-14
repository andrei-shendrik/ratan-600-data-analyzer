from dataclasses import dataclass

import numpy as np


@dataclass
class KurtosisData:
    """
            c0 1-2 GHz
            c1 2-3 GHz
    """
    _c0p0_kurt: np.ndarray
    _c0p1_kurt: np.ndarray
    _c1p0_kurt: np.ndarray
    _c1p1_kurt: np.ndarray

    @property
    def c0p0_kurt(self):
        return self._c0p0_kurt

    @c0p0_kurt.setter
    def c0p0_kurt(self, value):
        self._c0p0_kurt = value

    @property
    def c0p1_kurt(self):
        return self._c0p1_kurt

    @c0p1_kurt.setter
    def c0p1_kurt(self, value):
        self._c0p1_kurt = value

    @property
    def c1p0_kurt(self):
        return self._c1p0_kurt

    @c1p0_kurt.setter
    def c1p0_kurt(self, value):
        self._c1p0_kurt = value

    @property
    def c1p1_kurt(self):
        return self._c1p1_kurt

    @c1p1_kurt.setter
    def c1p1_kurt(self, value):
        self._c1p1_kurt = value