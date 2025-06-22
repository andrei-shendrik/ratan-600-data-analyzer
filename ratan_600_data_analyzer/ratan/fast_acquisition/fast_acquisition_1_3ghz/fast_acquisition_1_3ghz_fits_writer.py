from pathlib import Path

import numpy as np
from astropy.io import fits

from ratan_600_data_analyzer.common.project_info import ProjectInfo
from ratan_600_data_analyzer.ratan.data_receiver import DataReceiver
from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation
from ratan_600_data_analyzer.ratan.ratan_observation_writer import RatanObservationWriter


class FastAcquisition1To3GHzFitsWriter(RatanObservationWriter):
    def __init__(self, observation: RatanObservation):
        super().__init__(observation)

    @staticmethod
    def supports(data_receiver, file_type) -> bool:
        return (data_receiver == DataReceiver.FAST_ACQUISITION_1_3GHZ
                and file_type.lower() == ".fits")

    def write(self, output_file: Path):

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

        parent_dir = output_file.parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)

        # Header Data Unit
        # hdu 1
        primary_hdu = fits.PrimaryHDU(data=self.observation.data.array_3d.astype(np.float32))

        header = primary_hdu.header

        project_info = ProjectInfo()

        header["SIMPLE"] = (True, f"Written by {project_info.project_name} v{project_info.project_version}")

        # naxis пишутся автоматом при создании фитса, можно не заполнять.
        # header['NAXIS'] = self._data.ndim
        #     for i, dim in enumerate(self._data.shape):
        #         header[f'NAXIS{i + 1}'] = dim

        # todo
        header["TELESCOP"] = self.observation.metadata.telescope
        header["ORIGIN"] = DataReceiver.FAST_ACQUISITION_1_3GHZ.value
        header["BAND"] = "1-3 GHz"
        header['DATE-OBS'] = self.observation.metadata.datetime_culmination_local.strftime('%Y-%m-%d')
        header["TIME-OBS"] = self.observation.metadata.datetime_culmination_local.strftime('%H:%M:%S')
        header['CULM_EFR'] = (self.observation.metadata.azimuth, "Culmination by EFRAT")  #
        header['CULM_FEE'] = (self.observation.metadata.azimuth, "Culmination with Feed Horn Offset")
        header['T_START'] = self.observation.metadata.azimuth
        header['T_STOP'] = self.observation.metadata.azimuth

        header['OBJECT'] = self.observation.metadata.observation_object
        header['AZIMUTH'] = self.observation.metadata.azimuth
        header['ALTITUDE'] = self.observation.metadata.altitude
        header['SOL_DEC'] = self.observation.metadata.solar_declination
        header['SOL_RA'] = self.observation.metadata.solar_ra
        header['SOLAR_R'] = self.observation.metadata.solar_r
        header['SOLAR_P'] = self.observation.metadata.solar_p
        header['SOLAR_B'] = self.observation.metadata.solar_b

        # todo
        header['FEED_OFF'] = (self.observation.metadata.azimuth, "Feed Horn Offset, cm")
        header['FE_OFF_T'] = (self.observation.metadata.azimuth, "Feed Horn Offset by Time")

        # todo
        header['CALIBR'] = self.observation.metadata.azimuth
        header['ALIGNPA'] = (self.observation.metadata.azimuth, "Quiet sun alignment") # align_file_path
        header['UNITS'] = ("s.f.u.", "Data units")
        header['POLAR'] = ("Left / Right", "Polarization") # IV LR
        header['CLEAN'] = (False, "Additional data cleaning")

        header['CDELT1'] = self.observation.metadata.azimuth
        header['CRPIX1'] = self.observation.metadata.azimuth
        header['NSAMPLES'] = self.observation.metadata.azimuth
        header['NFREQS'] = self.observation.metadata.azimuth

        header['DTIME'] = (False, "Sampling time resolution, s")
        header['DACTIME'] = (False, "Actual time resolution, s")
        header['DFREQ'] = (False, "Frequency resolution, MHz")

        # todo
        header['KURTOSIS'] = (False, "Half wide of kurtosis interval")
        header['ATT1'] = (self.observation.metadata.azimuth, "Common attenuation")  #
        header['ATT2'] = (self.observation.metadata.azimuth, "1-2 GHz channels attenuation")
        header['ATT3'] = (self.observation.metadata.azimuth, "2-3 GHz channels attenuation")

        """
            np.uint8	8
            np.int16	16
            np.int32	32
            np.int64	64
            np.float32	-32
            np.float64	-64
        """

        # hdu 2
        col = fits.Column(
            name='freq',
            format='D',  # 8-byte double (float64)
            array=self.observation.metadata.data_layout.frequency_axis
            # array=np.array(self._metadata.frequencies))
        )
        table_hdu = fits.BinTableHDU.from_columns([col])

        # todo
        # добавить куртозис в новый hdu

        hdu_list = fits.HDUList([primary_hdu, table_hdu])
        hdu_list.writeto(output_file, overwrite=True)

    @property
    def observation(self):
        return self._observation