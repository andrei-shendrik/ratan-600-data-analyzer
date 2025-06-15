import numpy as np


class ChannelData:

    """
    S Вектор поляризации электромагнитных волн
    Параметры Стокса -- набор величин его описывающих
    Вектор S = S0 S1 S2 S3 = I Q U V

    Stokes I полная интенсивность
    Stokes V разность интенсивностей правой (RHCP) и левой (LHCP) круговых поляризаций

    В параметрах Стокса
    LHCP = (1 0 0 -1)
    RHCP = (1 0 0 1)

    I = LHCP + RHCP
    V = RHCP - LHCP

    LHCP = (I - V) / 2
    RHCP = (I + V) / 2
    __
    file = Path("file.fits")
    observation = Observation(file)
    data_extractor = DataExtractor(observation)
    channel_data = data_extractor.get_channel_data(frequency, stokes_i)

    extractor = DataExtractor()
    time_series = extractor.extract_time_series(observation, frequency=10, polarization=0)

    extractor = SimpleDataExtractor(observation)
    time_series = extractor.extract_time_series(frequency=10, polarization=0)

    """

    def __init__(self, frequency, polarization, array):
        self._frequency = frequency
        self._polarization = polarization
        self._array = array

    @property
    def frequency(self):
        return self._frequency

    @property
    def polarization(self):
        return self._polarization

    @property
    def array(self):
        return self._array