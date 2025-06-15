import numpy as np

from ratan_600_data_analyzer.ratan.channel_data import ChannelData
from ratan_600_data_analyzer.ratan.polarization_type import PolarizationType
from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation


class DataExtractor:
    def __init__(self, observation: RatanObservation):
        self._observation = observation

    def _get_closest_frequency(self, frequency: float) -> float:
        frequencies = self._observation.metadata.frequencies
        closest_frequency = min(frequencies, key=lambda f: abs(f - frequency))
        return closest_frequency

    def get_channel_data(self, frequency: float, polarization: PolarizationType) -> ChannelData:

        closest_frequency = self._get_closest_frequency(frequency)
        data_layout = self._observation.metadata.data_layout
        idx_freq = data_layout.get_frequency_index(closest_frequency)
        idx_pol = data_layout.get_polarization_index(polarization)
        array_3d = self._observation.data.array_3d
        channel_array = array_3d[idx_freq][idx_pol]
        return ChannelData(closest_frequency, polarization, channel_array)

    def set_channel_data(self, frequency: float, data_type: str, array: np.ndarray):

        """

        """
        #self._data[(frequency, data_type)] = array
        #self._frequencies.add(frequency)
        pass