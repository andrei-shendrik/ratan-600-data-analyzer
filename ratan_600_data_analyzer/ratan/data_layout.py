import numpy as np

from ratan_600_data_analyzer.ratan.polarization_type import PolarizationType


class DataLayout:
    """
        Структура массива array_3d данных наблюдения

        axes -- порядок осей в массиве
        frequency_axis -- список частот, соответствующий их порядку в массиве
        polarization_axis -- список поляризаций, соответствующий их порядку в массиве
    """
    def __init__(self, axes, frequency_axis, polarization_axis):
        self._axes = axes
        self._frequency_axis = frequency_axis
        self._polarization_axis = polarization_axis

    def get_frequency_index(self, frequency) -> int:

        indices = np.where(self._frequency_axis == frequency)[0]
        if len(indices) == 0:
            raise ValueError(f"Frequency {frequency} not found in DataLayout")
        return int(indices[0])

    def get_polarization_index(self, polarization: PolarizationType) -> int:

        mask = np.array(self._polarization_axis) == polarization
        indices = np.where(mask)[0]

        if len(indices) == 0:
            raise ValueError(f"Polarization {polarization} not found in DataLayout")
        return int(indices[0])