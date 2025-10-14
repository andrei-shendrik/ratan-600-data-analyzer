from dataclasses import dataclass

import numpy as np


@dataclass
class GeneratorStateData:
    """
            c0 1-2 GHz
            c1 2-3 GHz
    """
    _c0p0_state: np.ndarray
    _c0p1_state: np.ndarray
    _c1p0_state: np.ndarray
    _c1p1_state: np.ndarray

    @property
    def c0p0_state(self):
        return self._c0p0_state

    @c0p0_state.setter
    def c0p0_state(self, value):
        self._c0p0_state = value

    @property
    def c0p1_state(self):
        return self._c0p1_state

    @c0p1_state.setter
    def c0p1_state(self, value):
        self._c0p1_state = value

    @property
    def c1p0_state(self):
        return self._c1p0_state

    @c1p0_state.setter
    def c1p0_state(self, value):
        self._c1p0_state = value

    @property
    def c1p1_state(self):
        return self._c1p1_state

    @c1p1_state.setter
    def c1p1_state(self, value):
        self._c1p1_state = value