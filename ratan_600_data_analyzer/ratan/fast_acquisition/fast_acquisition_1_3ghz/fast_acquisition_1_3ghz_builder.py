from __future__ import annotations

import copy
import warnings
from pathlib import Path

import numpy as np

from ratan_600_data_analyzer.ratan.data_receiver import DataReceiver
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz import fast_input
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_configuration import \
    config
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import \
    FastAcquisition1To3GHzObservation
from ratan_600_data_analyzer.ratan.ratan_calibrator_factory import RatanCalibratorFactory
from ratan_600_data_analyzer.ratan.ratan_observation_builder import RatanObservationBuilder
from ratan_600_data_analyzer.ratan.ratan_reader_factory import RatanReaderFactory


class FastAcquisition1To3GHzBuilder(RatanObservationBuilder):
    def __init__(self, file: Path):
        super().__init__(file)
        self._observation = None

    @property
    def receiver(self) -> DataReceiver:
        return self._receiver

    @receiver.setter
    def receiver(self, value):
        self._receiver = value

    def build(self) -> FastAcquisition1To3GHzObservation:
        return self._observation

    def read(self) -> FastAcquisition1To3GHzBuilder:
        reader = RatanReaderFactory.create_reader(self._file)
        observation = reader.read(self._file)

        self._observation = observation
        return self

    def remove_spikes(self, method: str="kurtosis") -> FastAcquisition1To3GHzBuilder:
        """
            Remove spikes and zeros, changing to nan
        """
        if method.lower() == "kurtosis":
            observation = self._observation
            pol_chan_raw_data = observation.raw_data.polarization_channels_data
            kurtosis_data = observation.raw_data.kurtosis_data

            # original
            # pol_chan_data.c0p0_data[kurtosis_data.c0p0_kurt <= KURT_THRESHOLD] = np.nan
            # pol_chan_data.c0p1_data[kurtosis_data.c0p1_kurt <= KURT_THRESHOLD] = np.nan
            # pol_chan_data.c1p0_data[kurtosis_data.c1p0_kurt <= KURT_THRESHOLD] = np.nan
            # pol_chan_data.c1p1_data[kurtosis_data.c1p1_kurt <= KURT_THRESHOLD] = np.nan

            """
                kurtosis replace by 1
            """
            pol_chan_raw_data.c0p0_data[(kurtosis_data.c0p0_kurt <= config.kurt_threshold)
                                    & (pol_chan_raw_data.c0p0_data != config.raw_missing_value_replacement)] = config.raw_kurtosis_value_replacement
            pol_chan_raw_data.c0p1_data[(kurtosis_data.c0p1_kurt <= config.kurt_threshold)
                                    & (pol_chan_raw_data.c0p1_data != config.raw_missing_value_replacement)] = config.raw_kurtosis_value_replacement
            pol_chan_raw_data.c1p0_data[(kurtosis_data.c1p0_kurt <= config.kurt_threshold)
                                    & (pol_chan_raw_data.c1p0_data != config.raw_missing_value_replacement)] = config.raw_kurtosis_value_replacement
            pol_chan_raw_data.c1p1_data[(kurtosis_data.c1p1_kurt <= config.kurt_threshold)
                                    & (pol_chan_raw_data.c1p1_data != config.raw_missing_value_replacement)] = config.raw_kurtosis_value_replacement

            joined_channels_0 = np.hstack(
                (np.fliplr(pol_chan_raw_data.c0p0_data), pol_chan_raw_data.c1p0_data)).T  # 1-3 GHz pol0
            joined_channels_1 = np.hstack(
                (np.fliplr(pol_chan_raw_data.c0p1_data), pol_chan_raw_data.c1p1_data)).T  # 1-3 GHz pol1

            fast_acq_data = observation.data
            fast_acq_data.pol_channel0 = joined_channels_0
            fast_acq_data.pol_channel1 = joined_channels_1
            observation.data = fast_acq_data
            self._observation = copy.deepcopy(observation)
            return self
        raise ValueError(f"Spikes removing method {method} not found.")

    # todo
    # def time_downsample(self, time_reduction_factor: int) -> FastAcquisition1To3GHzBuilder:
    #
    #     pol_chan_data = self._observation.data.pol_channels_data
    #     joined_channels_0 = np.hstack((np.fliplr(pol_chan_data.c0p0_data), pol_chan_data.c1p0_data)).T  # 1-3 GHz pol0
    #     joined_channels_1 = np.hstack((np.fliplr(pol_chan_data.c0p1_data), pol_chan_data.c1p1_data)).T  # 1-3 GHz pol1
    #
    #     pol0_data = self._trim_polarization_array(joined_channels_0, time_reduction_factor = time_reduction_factor)
    #     pol1_data = self._trim_polarization_array(joined_channels_1, time_reduction_factor = time_reduction_factor)
    #
    #     array_3d = np.stack([pol0_data, pol1_data], axis=1)
    #
    #     fast_acq_data = FastAcquisition1To3GHzData()
    #     fast_acq_data.pol_channels_data = pol_chan_data
    #     fast_acq_data.kurtosis_data = self._data.kurtosis_data
    #     fast_acq_data.gen_state_data = self._data.gen_state_data
    #     fast_acq_data.array_3d = array_3d
    #
    #     bin_file = self._metadata.bin_file
    #     fast_acq_metadata = FastAcquisition1To3GHzMetadataBinLoader.load(bin_file, fast_acq_data)
    #
    #     self._metadata = fast_acq_metadata
    #     self._data = fast_acq_data
    #     return self

    @staticmethod
    def _trim_polarization_array(pol_array: np.ndarray, time_reduction_factor: int) -> np.ndarray:
        # Приводит массив к размеру, кратному self.time_reduction_factor, усредняет его по времени и заменяет
        # возможные nan интерполированными значениями

        n_bands, n_points = np.shape(pol_array)
        pol_array = pol_array[:, :(n_points // time_reduction_factor) * time_reduction_factor]
        try:
            pol_array = pol_array.reshape(n_bands, n_points // time_reduction_factor, -1)
            with warnings.catch_warnings():
                warnings.filterwarnings(action='ignore', message='Mean of empty slice')
                pol_array = np.nanmean(pol_array, axis=2)
            pol_array = fast_input.replace_nan(pol_array)
        except ValueError:
            pol_array = None
        return pol_array

    # todo
    # def interpolate_gaps(self, method: str) -> FastAcquisition1To3GHzBuilder:
    #     if method == "linear":
    #         """
    #             replace_nan заполняет nan значениями, полученными линейной интерполяцией между крайними значениями соседних
    #             промежутков. В fast_input есть функция replace_nan_interp, которая вычисляет средние по соседним промежуткам
    #             и интерполирует между этими средними, что кажется более корректным; кроме того, она может добавлять к
    #             интерполированным значениям гауссовский шум с мощностью, равной среднему арифметическому мощности шума в
    #             соседних промежутках. Естественно, все это работает гораздо медленнее.
    #         """
    #
    #         pol_chan_data = self._data.pol_channels_data
    #
    #         ch0_pol0 = fast_input.replace_nan(pol_chan_data.c0p0_data)
    #         ch0_pol1 = fast_input.replace_nan(pol_chan_data.c0p1_data)
    #         ch1_pol0 = fast_input.replace_nan(pol_chan_data.c1p0_data)
    #         ch1_pol1 = fast_input.replace_nan(pol_chan_data.c1p1_data)
    #
    #         pol_chan_data.c0p0_data = ch0_pol0
    #         pol_chan_data.c0p1_data = ch0_pol1
    #         pol_chan_data.c1p0_data = ch1_pol0
    #         pol_chan_data.c1p1_data = ch1_pol1
    #
    #         joined_channels_0 = np.hstack(
    #             (np.fliplr(pol_chan_data.c0p0_data), pol_chan_data.c1p0_data)).T  # 1-3 GHz pol0
    #         joined_channels_1 = np.hstack(
    #             (np.fliplr(pol_chan_data.c0p1_data), pol_chan_data.c1p1_data)).T  # 1-3 GHz pol1
    #         array_3d = np.stack([joined_channels_0, joined_channels_1], axis=1)
    #
    #         fast_acq_data = FastAcquisition1To3GHzData()
    #         fast_acq_data.pol_channels_data = pol_chan_data
    #         fast_acq_data.kurtosis_data = self._data.kurtosis_data
    #         fast_acq_data.gen_state_data = self._data.gen_state_data
    #         fast_acq_data.array_3d = array_3d
    #
    #         bin_file = self._metadata.bin_file
    #         desc_file = self._metadata.desc_file
    #         fast_acq_metadata = FastAcquisition1To3GHzMetadataBinLoader.load(desc_file, bin_file, fast_acq_data)
    #
    #         self._metadata = fast_acq_metadata
    #         self._data = fast_acq_data
    #         return self
    #     raise ValueError(f"Interpolation method {method} not found.")

    def calibrate(self, method: str) -> FastAcquisition1To3GHzBuilder:

        calibrator = RatanCalibratorFactory.create_calibrator(self._observation, "lebedev")
        observation = calibrator.calibrate()

        self._observation = observation
        return self

