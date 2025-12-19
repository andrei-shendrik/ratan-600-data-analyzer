import gzip
from pathlib import Path

import numpy as np

from ratan_600_data_analyzer.observation.observation import Observation
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz import fast_input
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_configuration import \
    config
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_data import \
    FastAcquisition1To3GHzData
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_metadata_bin_loader import \
    FastAcquisition1To3GHzMetadataBinLoader
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import \
    FastAcquisition1To3GHzObservation
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.raw_data.fast_acquisition_1_3ghz_raw_data import \
    FastAcquisition1To3GHzRawData
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.raw_data.generator_state_data import \
    GeneratorStateData
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.raw_data.kurtosis_data import KurtosisData
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.raw_data.polarization_channels_data import \
    PolarizationChannelsData
from ratan_600_data_analyzer.ratan.polarization_type import PolarizationType
from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation
from ratan_600_data_analyzer.ratan.ratan_observation_reader import RatanObservationReader


class FastAcquisition1To3GHzBinReader(RatanObservationReader):

    def can_read(self, file: Path):

        extensions = file.suffixes

        if extensions == ['.bin', '.gz']:
            return True
        elif extensions == ['.bin']:
            return True
        else:
            return False

    def read(self, bin_file: Path) -> RatanObservation:

        """
            склейки
            c0 1-2
            c1 2-3
            p0
            p1
        """
        pol_chan_data, kurtosis_data, gen_state_data = self._get_data_from_file(bin_file)

        """
            Missing values = 2
        """
        # pol_chan_data.c0p0_data = np.nan_to_num(pol_chan_data.c0p0_data, nan=replacement_value)
        # pol_chan_data.c0p1_data = np.nan_to_num(pol_chan_data.c0p1_data, nan=replacement_value)
        # pol_chan_data.c1p0_data = np.nan_to_num(pol_chan_data.c1p0_data, nan=replacement_value)
        # pol_chan_data.c1p1_data = np.nan_to_num(pol_chan_data.c1p1_data, nan=replacement_value)
        pol_chan_data.c0p0_data[pol_chan_data.c0p0_data == 0] = config.raw_missing_value_replacement
        pol_chan_data.c0p1_data[pol_chan_data.c0p1_data == 0] = config.raw_missing_value_replacement
        pol_chan_data.c1p0_data[pol_chan_data.c1p0_data == 0] = config.raw_missing_value_replacement
        pol_chan_data.c1p1_data[pol_chan_data.c1p1_data == 0] = config.raw_missing_value_replacement

        joined_channels_0 = np.hstack((np.fliplr(pol_chan_data.c0p0_data), pol_chan_data.c1p0_data)).T  # 1-3 GHz pol0
        joined_channels_1 = np.hstack((np.fliplr(pol_chan_data.c0p1_data), pol_chan_data.c1p1_data)).T  # 1-3 GHz pol1

        fast_acq_raw_data = FastAcquisition1To3GHzRawData()
        fast_acq_raw_data.polarization_channels_data = pol_chan_data
        fast_acq_raw_data.kurtosis_data = kurtosis_data
        fast_acq_raw_data.generator_state_data = gen_state_data

        polarization_to_attribute = {
            PolarizationType.LHCP.value: 'lhcp',
            PolarizationType.RHCP.value: 'rhcp'
        }
        channel_mapping = {
            'pol_channel0': polarization_to_attribute[config.pol_ch0],
            'pol_channel1': polarization_to_attribute[config.pol_ch1],
        }

        fast_acq_data = FastAcquisition1To3GHzData(channel_mapping)
        fast_acq_data.pol_channel0 = joined_channels_0
        fast_acq_data.pol_channel1 = joined_channels_1

        fast_acq_metadata = FastAcquisition1To3GHzMetadataBinLoader.load(bin_file, fast_acq_data=fast_acq_data, fast_acq_raw_data=fast_acq_raw_data)
        observation = FastAcquisition1To3GHzObservation(metadata=fast_acq_metadata, data=fast_acq_data, raw_data=fast_acq_raw_data)
        return observation

    def read_metadata(self, file_path: Path) -> Observation:
        pass

    def _get_data_from_file(self, file: Path, remove_spikes=True):

        """
            Если файл - архив, распаковываен и читаем данные в соответствии с форматом fast_input.dt;
            если не архив, просто читаем
        """

        file_name = file.name
        extensions = file.suffixes

        if extensions == ['.bin', '.gz']:
            try:
                with gzip.open(file) as f:
                    block_array = np.frombuffer(f.read(), dtype=fast_input.dt)
            except Exception as e:
                raise RuntimeError(f"_get_data_from_file(): {e}") from e
        elif extensions == ['.bin']:
            try:
                block_array = np.fromfile(file, dtype=fast_input.dt)
            except Exception as e:
                raise RuntimeError(f"_get_data_from_file(): {e}") from e
        else:
            raise ValueError(f"Unsupported file type: '{file_name}'.")

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

        pol_chan_data = PolarizationChannelsData(_c0p0_data=c0p0_data,
                                                 _c0p1_data=c0p1_data,
                                                 _c1p0_data=c1p0_data,
                                                 _c1p1_data=c1p1_data)

        kurtosis_data = KurtosisData(_c0p0_kurt=c0p0_kurtosis,
                                     _c0p1_kurt=c0p1_kurtosis,
                                     _c1p0_kurt=c1p0_kurtosis,
                                     _c1p1_kurt=c1p1_kurtosis)

        gen_state_data = GeneratorStateData(_c0p0_state=c0p0_state,
                                       _c0p1_state=c0p1_state,
                                       _c1p0_state=c1p0_state,
                                       _c1p1_state=c1p1_state)

        return pol_chan_data, kurtosis_data, gen_state_data

    def _get_polarization_arrays(self, raw_array, channel):
        def _align_to_chunk_length(length):
            return ((length + 1) // config.chunk_length) * config.chunk_length

        # Select elements of the channel
        if channel == 0:
            a = raw_array[raw_array['channel'] == 0]
        elif channel == 1:
            a = raw_array[raw_array['channel'] != 0]
        else:
            raise ValueError(f'Bad channel number: {channel}. Must be 0 or 1.')

        # Separate two polarizations
        p0 = a[(a['state'] & config.polarization_mask) == 0]
        p1 = a[(a['state'] & config.polarization_mask) != 0]

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
        r_p0 = np.zeros(p0_length, dtype=config.dt)
        r_p0[p0['cnt']] = p0
        r_p1 = np.zeros(p1_length, dtype=config.dt)
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