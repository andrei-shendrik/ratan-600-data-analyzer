from abc import ABC, abstractmethod


class CalibrationCoefficients(ABC):
    def __init__(self):
        self._calibration_coefficients_lhcp = None
        self._calibration_coefficients_rhcp = None
        self._calibration_coefficients_stokes_i = None
        self._calibration_coefficients_stokes_v = None

    @property
    @abstractmethod
    def calibration_coefficients_lhcp(self):
        pass

    @calibration_coefficients_lhcp.setter
    @abstractmethod
    def calibration_coefficients_lhcp(self, array):
        pass

    @property
    @abstractmethod
    def calibration_coefficients_rhcp(self):
        pass

    @calibration_coefficients_rhcp.setter
    @abstractmethod
    def calibration_coefficients_rhcp(self, array):
        pass