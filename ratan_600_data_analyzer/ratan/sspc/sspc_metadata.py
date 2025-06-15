import copy
import math
from datetime import datetime, timezone

import numpy as np

from ratan_600_data_analyzer.logger.logger import logger
from ratan_600_data_analyzer.ratan.axis import Axis
from ratan_600_data_analyzer.ratan.data_layout import DataLayout
from ratan_600_data_analyzer.ratan.polarization_type import PolarizationType
from ratan_600_data_analyzer.ratan.ratan_observation_metadata import RatanObservationMetadata
from ratan_600_data_analyzer.ratan.sspc.sspc_constants import SSPC_16_START_DATE
from ratan_600_data_analyzer.utils.date_utils import DateUtils


class SSPCMetadata(RatanObservationMetadata):

    """
        Solar spectral polarization complex (SSPC-16) metadata

        frequencies, polarizations, frequencies_wideband не дают соответствие расположению в массиве data,
        а определяют список доступных частот и поляризаций (порядок значения не имеет)

        Обращение к элементам массива array_3d организовано через DataLayout(), где имеет место порядок элементов


        header parameters
        SIMPLE  =                    T / Written by TFitsHdr (GVI 2005)
        BITPIX  =                   32 /
        EXTEND  =                    T / FITS data may contain extensions
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

    def __init__(self):
        super().__init__()

        self._data_receiver = None

        self._altitude = None
        self._azimuth = None
        self._cdelt1 = None
        self._datetime_culmination_local = None
        self._declination = None
        self._is_bad = None
        self._is_calibrated = None
        self._observation_object = None
        self._polarization_components = None
        self._right_ascension = None
        self._solar_b_angle = None
        self._solar_position_angle = None
        self._solar_radius = None
        self._telescope = None

        self._file = None
        self._data_receiver = None
        self._data_file_extension = None

        self._datetime_reg_start_utc = None
        self._datetime_reg_start_local = None

        self._datetime_culmination_utc = None
        self._datetime_culmination_local = None

        self._datetime_reg_stop_utc = None
        self._datetime_reg_stop_local = None

        self._frequencies = None  # narrowband only
        self._frequencies_wideband = None
        self._polarizations = None

        self._data_layout = None

        self._samples = None

        self._position_angle = None
        self._solar_declination = None

        self._solar_r = None

        self._adc_rate = None
        self._is_bad = None

        # fits header parameters
        self._header = None
        self._hdu2_table = None

        self._date_obs = None
        self._time_obs = None
        self._start_obs = None
        self._stop_obs = None
        self._crpix1 = None
        self._cdelt1 = None
        self._naxis = None
        self._naxis1 = None
        self._naxis2 = None
        self._naxis3 = None
        self._object = None
        self._azimuth = None
        self._telescope = None
        self._flag_iv = None
        self._is_calibrated = None

    @property
    def date_obs(self):
        return self._date_obs

    @date_obs.setter
    def date_obs(self, date_obs):
        self._date_obs = date_obs

    @property
    def frequencies(self):
        return self._frequencies

    @frequencies.setter
    def frequencies(self, frequencies):
        self._frequencies = frequencies

    @property
    def data_layout(self):
        return self._data_layout

    @data_layout.setter
    def data_layout(self, data_layout):
        self._data_layout = data_layout

    @property
    def data_receiver(self):
        return self._data_receiver

    @data_receiver.setter
    def data_receiver(self, value):
        self._data_receiver = value

    @property
    def data_file_extension(self):
        return self._data_file_extension

    @data_file_extension.setter
    def data_file_extension(self, value):
        self._data_file_extension = value

    @property
    def datetime_culmination_utc(self):
        return self._datetime_culmination_utc

    @datetime_culmination_utc.setter
    def datetime_culmination_utc(self, datetime_culmination_utc):
        self._datetime_culmination_utc = datetime_culmination_utc

    @property
    def altitude(self):
        return self._altitude

    @altitude.setter
    def altitude(self, value):
        self._altitude = value

    @property
    def azimuth(self):
        return self._azimuth

    @azimuth.setter
    def azimuth(self, value):
        self._azimuth = value

    @property
    def cdelt1(self):
        return self._cdelt1

    @cdelt1.setter
    def cdelt1(self, value):
        self._cdelt1 = value

    @property
    def datetime_culmination_local(self):
        return self._datetime_culmination_local

    @datetime_culmination_local.setter
    def datetime_culmination_local(self, value):
        self._datetime_culmination_local = value

    @property
    def declination(self):
        return self._declination

    @declination.setter
    def declination(self, value):
        self._declination = value

    @property
    def is_bad(self):
        return self._is_bad

    @is_bad.setter
    def is_bad(self, value):
        self._is_bad = value

    @property
    def is_calibrated(self):
        return self._is_calibrated

    @is_calibrated.setter
    def is_calibrated(self, value):
        self._is_calibrated = value

    @property
    def observation_object(self):
        return self._observation_object

    @observation_object.setter
    def observation_object(self, value):
        self._observation_object = value

    @property
    def polarization_components(self):
        return self._polarization_components

    @polarization_components.setter
    def polarization_components(self, value):
        self._polarization_components = value

    @property
    def right_ascension(self):
        return self._right_ascension

    @right_ascension.setter
    def right_ascension(self, value):
        self._right_ascension = value

    @property
    def solar_b_angle(self):
        return self._solar_b_angle

    @solar_b_angle.setter
    def solar_b_angle(self, value):
        self._solar_b_angle = value

    @property
    def solar_position_angle(self):
        return self._solar_position_angle

    @solar_position_angle.setter
    def solar_position_angle(self, value):
        self._solar_position_angle = value

    @property
    def solar_radius(self):
        return self._solar_radius

    @solar_radius.setter
    def solar_radius(self, value):
        self._solar_radius = value

    @property
    def telescope(self):
        return self._telescope

    @telescope.setter
    def telescope(self, value):
        self._telescope = value

    @property
    def datetime_reg_start_local(self):
        return self._datetime_reg_start_local

    @datetime_reg_start_local.setter
    def datetime_reg_start_local(self, value):
        self._datetime_reg_start_local = value

    @property
    def datetime_reg_start_utc(self):
        return self._datetime_reg_start_utc

    @datetime_reg_start_utc.setter
    def datetime_reg_start_utc(self, value):
        self._datetime_reg_start_utc = value

    @property
    def datetime_reg_stop_utc(self):
        return self._datetime_reg_stop_utc

    @datetime_reg_stop_utc.setter
    def datetime_reg_stop_utc(self, value):
        self._datetime_reg_stop_utc = value

    @property
    def polarizations(self):
        return self._polarizations

    @polarizations.setter
    def polarizations(self, value):
        self._polarizations = value