import copy

from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.raw_data.generator_state_data import \
    GeneratorStateData
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.raw_data.kurtosis_data import KurtosisData
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.raw_data.polarization_channels_data import \
    PolarizationChannelsData
from ratan_600_data_analyzer.ratan.ratan_observation_data import RatanObservationData


class FastAcquisition1To3GHzRawData:

    """
        Storage raw data of FastAcquisition 1-3GHz:
        polarizations (pol0,pol1)
        kurtosis (pol0,pol1)
        generator state (pol0,pol1)
    """

    def __init__(self, pol_channels_data: PolarizationChannelsData = None,
                 kurtosis_data: KurtosisData = None,
                gen_state_data: GeneratorStateData = None):
        self._polarization_channels_data = copy.deepcopy(pol_channels_data)
        self._kurtosis_data = copy.deepcopy(kurtosis_data)
        self._generator_state_data = copy.deepcopy(gen_state_data)

    @property
    def polarization_channels_data(self):
        return self._polarization_channels_data

    @polarization_channels_data.setter
    def polarization_channels_data(self, polarization_channels_data):
        self._polarization_channels_data = copy.deepcopy(polarization_channels_data)

    @property
    def kurtosis_data(self):
        return self._kurtosis_data

    @kurtosis_data.setter
    def kurtosis_data(self, kurtosis_data):
        self._kurtosis_data = copy.deepcopy(kurtosis_data)

    @property
    def generator_state_data(self):
        return self._generator_state_data

    @generator_state_data.setter
    def generator_state_data(self, generator_state_data):
        self._generator_state_data = copy.deepcopy(generator_state_data)