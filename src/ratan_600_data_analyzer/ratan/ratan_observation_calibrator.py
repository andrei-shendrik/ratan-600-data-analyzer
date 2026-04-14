from abc import ABC, abstractmethod

from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation


class RatanObservationCalibrator(ABC):

    def __init__(self, observation: RatanObservation):
        self._observation = observation

    @abstractmethod
    def calibrate(self):
        pass