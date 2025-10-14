import copy
from abc import abstractmethod, ABC

import numpy as np

from ratan_600_data_analyzer.observation.observation_data import ObservationData


class RatanObservationData(ObservationData, ABC):

    def __init__(self):
        self._lhcp = None
        self._rhcp = None
        self._stokes_i = None
        self._stokes_v = None

    @property
    @abstractmethod
    def lhcp(self):
        pass

    @lhcp.setter
    @abstractmethod
    def lhcp(self, array: np.ndarray):
        pass

    @property
    @abstractmethod
    def rhcp(self):
        pass

    @rhcp.setter
    @abstractmethod
    def rhcp(self, array: np.ndarray):
        pass

    @property
    @abstractmethod
    def stokes_i(self):
        pass

    @stokes_i.setter
    @abstractmethod
    def stokes_i(self, array: np.ndarray):
        pass

    @property
    @abstractmethod
    def stokes_v(self):
        pass

    @stokes_v.setter
    @abstractmethod
    def stokes_v(self, array: np.ndarray):
        pass