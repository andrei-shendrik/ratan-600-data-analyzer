from pathlib import Path

import numpy as np
from astropy.io import fits


class FitsCompatibilityWriter:

    """
        todo
        Запись в fits файл данных быстрого сбора в режиме совместимости с комплексом ССШК-16 (с его стандартной шапкой).
        С понижением частотного и временного разрешения.
        В целях работы в workscan и аналогичными программами (в режиме тестирования)

    """
    def __init__(self, observation):
        self._observation = observation
        self._metadata = observation.metadata
        self._data = observation.data

    def save(self, output_fits_file: Path):
        """

        """

        parent_dir = output_fits_file.parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)

        # Header Data Unit
        # hdu 1
        primary_hdu = fits.PrimaryHDU(data=self._data.astype(np.float32))

        header = primary_hdu.header

        header['NAXIS'] = self._data.ndim
        for i, dim in enumerate(self._data.shape):
            header[f'NAXIS{i + 1}'] = dim
        header["DATANAME"] = "newpas    "
        header["TELESCOP"] = self._metadata.telescope
        header["ORIGIN"] = "Python"
        header['DATE-OBS'] = self._metadata.datetime_culmination_local.strftime('%Y-%m-%d')
        header["TIME-OBS"] = self._metadata.datetime_culmination_local.strftime('%H:%M:%S')
        # test
        header["STARTOBS"] = 10000000
        header["STOPOBS"] = 20000000
        header["NSAMPLES"] = self._metadata.samples
        # LOSTPIXS
        header["ARMSMOOT"] = 0
        header["ARMDT"] = 0
        header["CRPIX1"] = 0
        header["CDELT1"] = 0
        header["FLAG_IV"] = self._metadata.flag_iv
        header["CALIBR"] = 0
        header["DSPDT"] = 0

        # COMMENT   *** Object parameters ***
        header['OBJECT'] = self._metadata.observation_object
        header['AZIMUTH'] = self._metadata.azimuth
        header['ALTITUDE'] = self._metadata.altitude
        header['SOL_DEC'] = self._metadata.solar_declination
        header['SOL_RA'] = self._metadata.solar_ra
        header['SOLAR_R'] = self._metadata.solar_r
        header['SOLAR_P'] = self._metadata.solar_p
        header['SOLAR_B'] = self._metadata.solar_b

        header['SMOOTH'] = 0

        """
            Пример новой шапки
            SIMPLE = T / conforms
            to
            FITS
            standard
            BITPIX = -64 / array
            data
            type NAXIS = 3 / number
            of
            array
            dimensions
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
            TELESCOP = 'RATAN_600' / DM
            complex
            UNITS = 'sfu     ' / Data
            units
            BAND = '1-3 GHz '
            POLAR = 'Left / Right' / Polarization
            CLEAN = 'no      ' / Additional
            data
            cleaning
            ALIGNPA = 'align_file_path' / Quiet
            sun
            alignment
            DTIME = 0.0083886 / Sampling
            time
            resolution, s
            DACTIME = 0.5 / Actual
            time
            resolution, s
            DFREQ = 3.904 / Frequency
            resolution, MHz
            KURTOSIS = 20 / Half
            wide
            of
            kurtosis
            interval
            ATT1 = -10 / Common
            attenuation
            ATT2 = 0 / 1 - 2
            GHz
            channel
            attenuation
            ATT3 = 0 / 2_3
            GHz
            channel
            attenuation
            COMMENT: NAXIS1 - IV - representation, I - ind
            0, V - ind
            1

            Шапка ССПК
            NAXIS   =                    3 /
            NAXIS1  =                 3001 /
            NAXIS2  =                    2 /
            NAXIS3  =                   90 /
            DATANAME= 'newpas  '           /
            TELESCOP= 'RATAN-600'          /
            ORIGIN  = 'PAS-120 '           /
            DATE-OBS= '2017/09/05'         /
            TIME-OBS= '12:12:17.400'       /
            STARTOBS=           1504602458 /
            STOPOBS =           1504603058 /
            NSAMPLES=                 3001 / NAXIS1 = (NSAMPLES + lostpixs)/SMOOTH
            LOSTPIXS=                    0 /
            SMOOTH  =                    1 /
            ARMSMOOT=                    1 /
            ARMDT   =             0.200000 /
            CRPIX1  =          1604.534912 /
            CDELT1  =   2.979664428742E+00 / arcsec
            FLAG_IV =                    1 / 1- data is RL; 0- data is IV
            CALIBR  =                    0 /
            COMMENT   *** Object parameters ***
            OBJECT  = 'sun     '           /
            AZIMUTH =             0.000000 /
            ALTITUDE=            52.806862 /
            SOL_DEC =             6.675000 /
            SOL_RA  =            10.956000 /
            SOLAR_R =           951.919983 / arcsec
            SOLAR_P =            22.100000 /
            SOLAR_B =             7.200000 /
            SOL_VALH=             0.000000 /
            COMMENT   *** Frequencies ***
            FREQ001 =            17.906250 / GHz
            FREQ002 =            17.718750 / GHz
            ...
            FREQ090 =             3.750000 / GHz
            END
        """

        # hdu 2
        col = fits.Column(
            name='freq',
            format='D',  # 8-byte double (float64)
            array=self._metadata.frequencies
            # array=np.array(self._metadata.frequencies))
        )
        table_hdu = fits.BinTableHDU.from_columns([col])
        hdu_list = fits.HDUList([primary_hdu, table_hdu])
        hdu_list.writeto(output_fits_file, overwrite=True)