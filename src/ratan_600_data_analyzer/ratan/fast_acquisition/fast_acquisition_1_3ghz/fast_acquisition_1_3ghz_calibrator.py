from abc import abstractmethod

from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import \
    FastAcquisition1To3GHzObservation
from ratan_600_data_analyzer.ratan.ratan_observation_calibrator import RatanObservationCalibrator


class FastAcquisition1To3GHzCalibrator(RatanObservationCalibrator):

    def __init__(self, observation: FastAcquisition1To3GHzObservation):
        super().__init__(observation)
        self._observation = observation

    @abstractmethod
    def calibrate(self):
        pass