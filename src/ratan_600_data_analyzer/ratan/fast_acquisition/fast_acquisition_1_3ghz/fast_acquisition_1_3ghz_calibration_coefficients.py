import copy

from ratan_600_data_analyzer.ratan.calibration_coefficients import CalibrationCoefficients


class FastAcquisitionCalibrationCoefficients(CalibrationCoefficients):
    def __init__(self, channel_mapping: dict):
        super().__init__()
        self._channel_mapping = channel_mapping
        self._calibration_coefficients_lhcp = None
        self._calibration_coefficients_rhcp = None
        self._calibration_coefficients_stokes_i = None
        self._calibration_coefficients_stokes_v = None

    @property
    def calibration_coefficients_lhcp(self):
        return self._calibration_coefficients_lhcp

    @calibration_coefficients_lhcp.setter
    def calibration_coefficients_lhcp(self, array):
        self._calibration_coefficients_lhcp = copy.deepcopy(array)

    @property
    def calibration_coefficients_rhcp(self):
        return self._calibration_coefficients_rhcp

    @calibration_coefficients_rhcp.setter
    def calibration_coefficients_rhcp(self, array):
        self._calibration_coefficients_rhcp = copy.deepcopy(array)

    @property
    def calibration_coefficients_pol_channel0(self):
        target_attr = self._channel_mapping['pol_channel0']
        return getattr(self, target_attr)

    @calibration_coefficients_pol_channel0.setter
    def calibration_coefficients_pol_channel0(self, array):
        target_attr = self._channel_mapping['pol_channel0']
        setattr(self, target_attr, array)

    @property
    def calibration_coefficients_pol_channel1(self):
        target_attr = self._channel_mapping['pol_channel1']
        return getattr(self, target_attr)

    @calibration_coefficients_pol_channel1.setter
    def calibration_coefficients_pol_channel1(self, array):
        target_attr = self._channel_mapping['pol_channel1']
        setattr(self, target_attr, array)