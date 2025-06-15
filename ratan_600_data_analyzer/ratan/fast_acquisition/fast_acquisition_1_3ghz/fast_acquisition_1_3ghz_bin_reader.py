import warnings
from pathlib import Path
import numpy as np

from ratan_600_data_analyzer.observation.observation import Observation
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz import fast_input
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_constants import dt, POLARIZATION_MASK, CHUNK_LENGTH, KURT_THRESHOLD, \
    TIME_REDUCTION_FACTOR
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_data import \
    FastAcquisition1To3GHzData
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_metadata_bin_loader import \
    FastAcquisition1To3GHzMetadataBinLoader
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import \
    FastAcquisition1To3GHzObservation
from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation
from ratan_600_data_analyzer.ratan.ratan_observation_reader import RatanObservationReader


class FastAcquisition1To3GHzBinReader(RatanObservationReader):

    def can_read(self, bin_file: Path):
        if not bin_file.suffix.lower() == '.bin':
            return False
        # try:
        #
        # except Exception:
        #     return False
        return True

    def read(self, bin_file: Path) -> RatanObservation:

        """
            склейки
            c0 1-2
            c1 2-3
            p0
            p1
        """

        c0p0_data, c0p1_data, c1p0_data, c1p1_data, \
            c0p0_kurtosis, c0p1_kurtosis, c1p0_kurtosis, c1p1_kurtosis, \
            c0p0_state, c0p1_state, c1p0_state, c1p1_state = self._get_data_from_file(bin_file)

        c0p0_data[c0p0_kurtosis <= KURT_THRESHOLD] = np.nan
        c0p1_data[c0p1_kurtosis <= KURT_THRESHOLD] = np.nan
        c1p0_data[c1p0_kurtosis <= KURT_THRESHOLD] = np.nan
        c1p1_data[c1p1_kurtosis <= KURT_THRESHOLD] = np.nan

        ch0_pol0 = fast_input.replace_nan(c0p0_data)
        ch0_pol1 = fast_input.replace_nan(c0p1_data)
        ch1_pol0 = fast_input.replace_nan(c1p0_data)
        ch1_pol1 = fast_input.replace_nan(c1p1_data)

        joined_channels_0 = np.hstack((np.fliplr(ch0_pol0), ch1_pol0)).T  # 1-3 GHz pol0
        joined_channels_1 = np.hstack((np.fliplr(ch0_pol1), ch1_pol1)).T  # 1-3 GHz pol1

        pol0_data = self._trim_polarization_array(joined_channels_0)
        pol1_data = self._trim_polarization_array(joined_channels_1)

        array_3d = np.stack([pol0_data, pol1_data], axis=1)

        desc_file = bin_file.with_suffix(".desc")
        fast_acq_metadata = FastAcquisition1To3GHzMetadataBinLoader.load(desc_file, bin_file, array_3d)
        fast_acq_data = FastAcquisition1To3GHzData(array_3d)
        observation = FastAcquisition1To3GHzObservation(fast_acq_metadata, fast_acq_data)

        return observation

    def read_metadata(self, file_path: Path) -> Observation:
        pass

    def _get_data_from_file(self, file, remove_spikes=True):
        block_array = np.fromfile(file, dtype=dt)

        return self._get_data(block_array, remove_spikes=True)

    def _get_data(self, block_array, remove_spikes=True):

        avg_num = 2 ** (block_array[0]['avg_kurt'] & 0b111111)
        spectrum_length = 8192 // avg_num

        chan0_pol0, chan0_pol1 = self._get_polarization_arrays(block_array, channel=0)
        chan1_pol0, chan1_pol1 = self._get_polarization_arrays(block_array, channel=1)

        if remove_spikes:
            chan0_length = min(chan0_pol0.shape[0], chan0_pol1.shape[0])
            if chan0_length > 0:
                chan0_pol0, chan0_pol1 \
                    = self._remove_spikes_from_polarization_arrays(chan0_pol0[:chan0_length], chan0_pol1[:chan0_length])
            chan1_length = min(chan1_pol0.shape[0], chan1_pol1.shape[0])
            if chan1_length > 0:
                chan1_pol0, chan1_pol1 \
                    = self._remove_spikes_from_polarization_arrays(chan1_pol0[:chan1_length], chan1_pol1[:chan1_length])

        c0p0_data, c0p0_kurtosis, c0p0_state = self._get_data_and_kurtosis(chan0_pol0, spectrum_length)
        c0p1_data, c0p1_kurtosis, c0p1_state = self._get_data_and_kurtosis(chan0_pol1, spectrum_length)
        c1p0_data, c1p0_kurtosis, c1p0_state = self._get_data_and_kurtosis(chan1_pol0, spectrum_length)
        c1p1_data, c1p1_kurtosis, c1p1_state = self._get_data_and_kurtosis(chan1_pol1, spectrum_length)

        return c0p0_data, c0p1_data, c1p0_data, c1p1_data, \
            c0p0_kurtosis, c0p1_kurtosis, c1p0_kurtosis, c1p1_kurtosis, \
            c0p0_state, c0p1_state, c1p0_state, c1p1_state

    def _get_polarization_arrays(self, raw_array, channel):
        def _align_to_chunk_length(length):
            return ((length + 1) // CHUNK_LENGTH) * CHUNK_LENGTH

        # Select elements of the channel
        if channel == 0:
            a = raw_array[raw_array['channel'] == 0]
        elif channel == 1:
            a = raw_array[raw_array['channel'] != 0]
        else:
            raise ValueError(f'Bad channel number: {channel}. Must be 0 or 1.')

        # Separate two polarizations
        p0 = a[(a['state'] & POLARIZATION_MASK) == 0]
        p1 = a[(a['state'] & POLARIZATION_MASK) != 0]

        # Find max frame numbers
        p0_maxindex = p0['cnt'].max() if p0.size > 0 else 0
        p1_maxindex = p1['cnt'].max() if p1.size > 0 else 0

        # Make the array size a multiple of chunk (ethernet frame payload) size throwing away any possible trailing trash
        p0_length = _align_to_chunk_length(p0_maxindex)
        p1_length = _align_to_chunk_length(p1_maxindex)
        p0 = p0[p0['cnt'] < p0_length]
        p1 = p1[p1['cnt'] < p1_length]

        # Construct zero arrays to accomodate the full data in the case when there are no missing values
        # and fill them with the available data
        r_p0 = np.zeros(p0_length, dtype=dt)
        r_p0[p0['cnt']] = p0
        r_p1 = np.zeros(p1_length, dtype=dt)
        r_p1[p1['cnt']] = p1

        return r_p0, r_p1

    def _get_data_and_kurtosis(self, a, spectrum_length):
        cc = a['data'].reshape(-1, spectrum_length)
        state = np.empty(a['data'].shape, dtype=np.uint32)
        for i in np.arange(0, state.shape[0]):
            state[i, :] = a['state'][i]
        state = state.reshape(-1, spectrum_length)
        return (cc & 0x7FFFFFFFFFFFFF).astype(np.float32), (cc >> 55).astype(np.float32), state

    def _remove_spikes_from_polarization_arrays(self, a, b, shift=-4):
        idx_a = np.roll((a['cnt'] > 0), shift, axis=0)
        idx_b = np.roll((b['cnt'] > 0), shift, axis=0)
        a[idx_b] = 0
        b[idx_a] = 0
        return a, b

    def _trim_polarization_array(self, pol_array: np.array):
        n_bands, n_points = np.shape(pol_array)
        pol_array = pol_array[:, :(n_points // TIME_REDUCTION_FACTOR) * TIME_REDUCTION_FACTOR]
        try:
            pol_array = pol_array.reshape(n_bands, n_points // TIME_REDUCTION_FACTOR, -1)
            with warnings.catch_warnings():
                warnings.filterwarnings(action='ignore', message='Mean of empty slice')
                pol_array = np.nanmean(pol_array, axis=2)
            pol_array = fast_input.replace_nan(pol_array)
        except ValueError:
            pol_array = None
        return pol_array