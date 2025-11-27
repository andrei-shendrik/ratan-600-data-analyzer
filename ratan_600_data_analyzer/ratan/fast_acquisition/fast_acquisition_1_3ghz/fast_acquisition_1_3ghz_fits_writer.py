from pathlib import Path

import numpy as np
from astropy.io import fits

from ratan_600_data_analyzer.common.project_info import ProjectInfo
from ratan_600_data_analyzer.ratan.data_receiver import DataReceiver
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import \
    FastAcquisition1To3GHzObservation
from ratan_600_data_analyzer.ratan.ratan_observation_writer import RatanObservationWriter


class FastAcquisition1To3GHzFitsWriter(RatanObservationWriter):
    def __init__(self, observation: FastAcquisition1To3GHzObservation):
        super().__init__(observation)
        self._observation = observation

    @staticmethod
    def supports(data_receiver, file_type) -> bool:
        return (data_receiver == DataReceiver.FAST_ACQUISITION_1_3GHZ
                and file_type.lower() == ".fits")

    def write(self, output_file: Path, overwrite: bool = False):

        """
            Комментарий: по стандарту FITS имя параметра в шапке не должно быть более 8 символов.

            Пример новой шапки
            SIMPLE = T / conforms to FITS standard
            BITPIX = -64 / array data type
            NAXIS = 3 / number of array dimensions
            NAXIS1 = 2
            NAXIS2 = 512
            NAXIS3 = 1586
            EXTEND = T
            OBJECT = 'sun     '
            T_OBS = '2024-02-22T12:27:09.540000+03:00'
            AZIMUTH = '+0      '
            ALTITUDE = '35.827639'
            DEC = '-10.318 '
            RA = '22.345  '
            SOLAR_R = '970.280 '
            SOLAR_P = '-19.500 '
            SOLAR_B = '-7.100  '
            OFF_TIME = '41.479349'
            TELESCOP = 'RATAN_600' / DM complex
            UNITS = 'sfu     ' / Data units
            BAND = '1-3 GHz '
            POLAR = 'Left / Right' / Polarization
            CLEAN = 'no      ' / Additional data cleaning
            ALIGNPA = 'align_file_path' / Quiet sun alignment
            DTIME = 0.0083886 / Sampling time resolution, s
            DACTIME = 0.5 / Actual time resolution, s
            DFREQ = 3.904 / Frequency resolution, MHz
            KURTOSIS = 20 / Half wide of kurtosis interval
            ATT1 = -10 / Common attenuation
            ATT2 = 0 / 1 - 2 GHz channel attenuation
            ATT3 = 0 / 2_3 GHz channel attenuation
            COMMENT: NAXIS1 - IV - representation, I - ind 0, V - ind 1
        """

        metadata = self.observation.metadata
        data = self.observation.data
        data_cube = np.stack([data.pol_channel0, data.pol_channel1], axis=1)
        #axes = [Axis.FREQUENCY, Axis.POLARIZATION, Axis.SAMPLE]

        parent_dir = output_file.parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)

        # Header Data Unit
        # hdu 1
        #primary_hdu = fits.PrimaryHDU(data=self.observation.data.array_3d.astype(np.float32))
        primary_hdu = fits.PrimaryHDU()

        # сжатие данных
        """
            Compression algorithm: one of
            ``'RICE_1'``, ``'RICE_ONE'``, ``'PLIO_1'``, ``'GZIP_1'``,
            ``'GZIP_2'``, ``'HCOMPRESS_1'``, ``'NOCOMPRESS'``

            Использовать int64 для исходных (сырых) некалиброванных данных. Отсчеты АЦП целые большие числа.    
            compressed_hdu = fits.CompImageHDU(data=array_3d.astype(np.int64),
                                            compression_type='GZIP_2')                            
            Для калиброванных float
            
            np.uint8	8
            np.int16	16
            np.int32	32
            np.int64	64
            np.float32	-32
            np.float64	-64
        """
        if metadata.is_calibrated:
            tile_shape = data_cube.shape # tile as entire image, slightly better accuracy
            compressed_hdu = fits.CompImageHDU(data=data_cube.astype(np.float32),
                                               compression_type='GZIP_2',
                                               quantize_level=128,
                                               tile_shape=tile_shape)
            #compressed_hdu = fits.ImageHDU(data=data_cube.astype(np.float32))
        else:
            compressed_hdu = fits.CompImageHDU(data=data_cube.astype(np.int64),
                                               compression_type='GZIP_2')

        header = primary_hdu.header

        project_info = ProjectInfo()

        header["SIMPLE"] = (True, f"Written by {project_info.project_name} v{project_info.project_version}")

        # naxis пишутся автоматом при создании фитса, можно не заполнять.
        # header['NAXIS'] = self._data.ndim
        #     for i, dim in enumerate(self._data.shape):
        #         header[f'NAXIS{i + 1}'] = dim

        header["TELESCOP"] = metadata.telescope
        header["ORIGIN"] = DataReceiver.FAST_ACQUISITION_1_3GHZ.value
        header["BAND"] = "1-3 GHz"
        header['DATE-OBS'] = metadata.datetime_culmination_feed_horn_local.strftime('%Y-%m-%d')
        header["TIME-OBS"] = metadata.datetime_culmination_feed_horn_local.strftime('%H:%M:%S')

        culm_efr_utc = metadata.datetime_culmination_efrat_utc
        header['CULM_EFR'] = (culm_efr_utc.isoformat(), f"Culmination by EFRAT, UTC")
        culm_feed_horn_utc = metadata.datetime_culmination_feed_horn_utc
        header['CULM_FEE'] = (culm_feed_horn_utc.isoformat(), f"Culmination FeedHorn Offset, UTC")

        header['T_START'] = (metadata.datetime_reg_start_utc.isoformat(), f"Observation Start Time, UTC")
        header['T_STOP'] = (metadata.datetime_reg_stop_utc.isoformat(), f"Observation Stop Time, UTC")

        header['OBJECT'] = metadata.observation_object
        header['AZIMUTH'] = metadata.azimuth
        if metadata.altitude is not None:
            header['ALTITUDE'] = (metadata.altitude.value, f"Unit: {metadata.altitude.unit}")
        header['SOL_DEC'] = (metadata.declination.value, f"Unit: {metadata.declination.unit}")
        header['SOL_RA'] = (metadata.right_ascension.value, f"Unit: {metadata.right_ascension.unit}")
        header['SOLAR_R'] = (metadata.solar_r.value, f"Unit: {metadata.solar_r.unit}")
        header['SOLAR_P'] = (metadata.solar_p.value, f"Unit: {metadata.solar_p.unit}")
        header['SOLAR_B'] = (metadata.solar_b.value, f"Unit: {metadata.solar_b.unit}")

        header['FEED_OFF'] = (metadata.feed_offset, "Feed Horn Offset, cm")
        header['FE_OFF_T'] = (metadata.feed_offset_time.total_seconds(), "Feed Horn Offset by Time, s")

        header['POL_CH0'] = data.channel_mapping["pol_channel0"].upper()
        header['POL_CH1'] = data.channel_mapping["pol_channel1"].upper()
        header['CALIBR'] = (metadata.is_calibrated, "Is calibrated")
        header['QSP'] = (metadata._quiet_sun_point_arcsec, "Quiet Sun Point, arcsec")
        #header['ALIGNPA'] = ("to#do", "Quiet sun alignment") # align_file_path
        header['UNIT'] = (metadata.unit, "Data unit")
        #header['POLAR'] = ("Left / Right", "Polarization") # IV LR
        header['CLEAN'] = (False, "Additional data cleaning")

        #header['CDELT1'] = metadata.cdelt1
        #header['CRPIX1'] = metadata.crpix1
        header['ARCPSAM'] = (metadata.arcsec_per_sample.value, "Arcsec per sample")
        header['ARCPSEC'] = (metadata.arcsec_per_second.value, "Arcsec per second")

        header['NSAMPLES'] = (metadata.num_samples, "Number of samples")
        header['NFREQS'] = (metadata.num_frequencies, "Number of frequencies")

        header['REF_TIME'] = (metadata.ref_time, f"Reference time culm, s")
        header['REF_SAMP'] = (metadata.ref_sample, f"Reference sample culm")

        header['DTIME'] = (metadata.time_resolution, "Sampling time resolution, s")
        header['DACTIME'] = (metadata.switch_polarization_time, "Actual time resolution, s")
        header['DFREQ'] = (metadata.frequency_resolution, "Frequency resolution, MHz")

        if metadata.half_width_kurtosis_interval is not None:
            header['KURTOSIS'] = (metadata.half_width_kurtosis_interval, "Half width of kurtosis interval")
        header['ATT1'] = (metadata.attenuator_common, "Common attenuation")
        header['ATT2'] = (metadata.attenuator_1_2ghz, "1-2 GHz channels attenuation")
        header['ATT3'] = (metadata.attenuator_2_3ghz, "2-3 GHz channels attenuation")

        # hdu 2
        col_freq = fits.Column(
            name='freq',
            format='D',  # 8-byte double (float64)
            array=metadata.coordinate_axes.frequency_axis
            # array=np.array(self._metadata.frequencies))
        )


        cal_coeffs = metadata.calibration_coefficients
        if cal_coeffs is not None:
            col_calibr_coeff_p0 = fits.Column(
                name='cal_p0',
                format='D',
                array=cal_coeffs.calibration_coefficients_pol_channel0
            )

            col_calibr_coeff_p1 = fits.Column(
                name='cal_p1',
                format='D',
                array=cal_coeffs.calibration_coefficients_pol_channel1
            )
            table_hdu = fits.BinTableHDU.from_columns([col_freq, col_calibr_coeff_p0, col_calibr_coeff_p1],
                                                      name='VALUES_TABLE')
        else:
            table_hdu = fits.BinTableHDU.from_columns([col_freq],
                                                      name='VALUES_TABLE')

        hdu_list = fits.HDUList([primary_hdu, compressed_hdu, table_hdu])
        hdu_list.writeto(output_file, overwrite=overwrite)

    @property
    def observation(self):
        return self._observation