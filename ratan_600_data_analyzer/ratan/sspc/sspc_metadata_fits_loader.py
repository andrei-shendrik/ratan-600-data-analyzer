import copy
import math
from datetime import datetime, timezone

import numpy as np

from ratan_600_data_analyzer.logger.logger import logger
from ratan_600_data_analyzer.ratan.axis import Axis
from ratan_600_data_analyzer.ratan.data_layout import DataLayout
from ratan_600_data_analyzer.ratan.fits_parameters_extractor import FitsParametersExtractor
from ratan_600_data_analyzer.ratan.fits_table_parameters_extractor import FitsTableParametersExtractor
from ratan_600_data_analyzer.ratan.polarization_type import PolarizationType
from ratan_600_data_analyzer.ratan.ratan_metadata_loader import RatanMetadataLoader
from ratan_600_data_analyzer.ratan.sspc.sspc_constants import SSPC_16_START_DATE
from ratan_600_data_analyzer.ratan.sspc.sspc_metadata import SSPCMetadata
from ratan_600_data_analyzer.utils.date_utils import DateUtils


class SSPCMetadataFitsLoader(RatanMetadataLoader):
    """
        Загружает параметры из шапки fits файла в поля объекта класса
    """

    @staticmethod
    def load(header, hdu2_table, array_3d) -> SSPCMetadata:

        metadata = SSPCMetadata()

        # header hdu1
        if header is None:
            raise RuntimeError(f"Header is none")

        metadata.header = copy.deepcopy(header)
        fits_param_extractor = FitsParametersExtractor(header)

        metadata.date_obs = fits_param_extractor.get_fits_header_value("DATE-OBS")
        metadata.time_obs = fits_param_extractor.get_fits_header_value("TIME-OBS")
        metadata.flag_iv = fits_param_extractor.get_fits_header_value("FLAG_IV")  # 1 - data is RL; 0 - data is IV
        metadata.start_obs = fits_param_extractor.get_fits_header_value("STARTOBS")
        metadata.stop_obs = fits_param_extractor.get_fits_header_value("STOPOBS")
        metadata.cdelt1 = fits_param_extractor.get_fits_header_value("CDELT1")
        if metadata.cdelt1 < 0.1:
            metadata._is_bad = True
        metadata.telescope = fits_param_extractor.get_fits_header_value("TELESCOP")
        metadata.naxis = fits_param_extractor.get_fits_header_value("NAXIS")
        metadata.naxis1 = fits_param_extractor.get_fits_header_value("NAXIS1")
        metadata.object = fits_param_extractor.get_fits_header_value("OBJECT")
        metadata.azimuth = fits_param_extractor.get_fits_header_value("AZIMUTH")
        calibr = fits_param_extractor.get_fits_header_value("CALIBR")
        if calibr == 1:
            metadata.is_calibrated = True
        else:
            metadata.is_calibrated = False

        metadata.crpix1 = fits_param_extractor.get_fits_header_value("CRPIX1")
        metadata.smooth = fits_param_extractor.get_fits_header_value("SMOOTH")
        metadata.armdt = fits_param_extractor.get_fits_header_value("ARMDT")

        metadata._solar_r = fits_param_extractor.get_fits_header_value("SOLAR_R")
        # self._solar_r *= SOLAR_R_COEFF

        """
            Solar Coordinates
            https://www.qsl.net/f5ru/glossary.htm
            http://jgiesen.de/sunrot/index.html
    
            P-angle (or P):
            The position angle between the geocentric north pole and the solar rotational north pole measured eastward from geocentric north.
            The range in P is +/- 26.3l degrees.
            Solar_P
    
            Bo (or B-angle):
            Heliographic latitude of the central point of the solar disk; also called the  B-angle. The range of Bo is +/- 7.23 degrees,
            correcting for the tilt of the ecliptic with respect to the solar equatorial plane.
            Solar_B
    
            Lo:
            Heliographic longitude of the central point of the solar disk.
        """

        metadata.solar_p = fits_param_extractor.get_fits_header_value("SOLAR_P")
        metadata.solar_b = fits_param_extractor.get_fits_header_value("SOLAR_B")

        metadata.solar_declination = fits_param_extractor.get_fits_header_value("SOL_DEC")

        """
            Формуля для расчета позиционного угла взята из работы:
            Тохчукова С.Х. Исследования Солнца на РАТАН-600 в многоазимутальном режиме, диссертация на соискание к.ф.-м.н., 2002
            2002_stokh_dissert.pdf
        """

        metadata.position_angle = -math.asin(
            math.tan(math.radians(metadata.azimuth)) *
            math.tan(math.radians(metadata.solar_declination))
        ) * 180 / math.pi

        # data
        dim1, dim2, dim3 = SSPCMetadataFitsLoader._get_data_dimensions(array_3d)
        metadata.samples = dim3

        # load time values
        """
            20170622 az0
            MAINOBS
            12:15:38.820 = culm_time время кульминации в mainobs по местному времени
            12:13:39.000 = regstart в mainobs
            5.00сек задержка в файле сценария до начала фактической регистрации
            z_sun_240 файл сценария, длительность регистрации 240.0сек

            FITS FILENAME
            121538 время в имени файла = время кульминации в mainobs (с точностью до секунды с округлением в меньшую сторону)

            FITS HEADER
            TIME-OBS = 12:15:38.820 // время кульминации
            STARTOBS = 1498122824 // linux время начала регистрации в UTC, отсчеты в секундах, в переводе 9:13:44 (с точностью до секунды)
            STOPOBS = 1498123064 // linux время конца регистрации в UTC, отсчеты в секундах, в переводе 9:17:44 (с точностью до секунды)
            NAXIS1 = 1201 // число отсчетов в FITS файле по времени (NAXIS1 = (NSAMPLES + lostpixs)/SMOOTH)
            NSAMPLES = число отсчетов в исходном RAW файле -- не использовать!!! В новой регистрации совпадает с NAXIS1. В старой регистрации порядка 30000 отсчетов на файл.
            SMOOTH = 1 // число усредняемых отсчетов. В новой регистрации усреднения нет smooth = 1.
            В старой регистрации smooth = 30. Т.е. для старой регистрации в FITS файле в 30 раз меньше отсчетов чем в RAW файле
            ARMDT = 0.200 // интервал времени в RAW файле между отсчетами в секундах. В старой регистрации ARMDT = 0.007
            Фактический интервал времени между отсчетами в FITS файле = ARMDT*SMOOTH
            CRPIX1 = 629.524963 // номер отсчета соответствующего времени кульминации (последний отсчет в файле соответствует первому по времени)
            CDELT1 = 2.752660490387 // число arcsec в одном отсчете

            1997, 2002 timeobs в UTC, startobs и т.д. отсутствует!
            TIME-OBS= '09:00:27.100'
            CRPIX1 = 535.593811
            STARTOBS нет
            STOPOBS нет
            SMOOTH отсутствует
            ARMDT(DSPDT) отсутствует

            2009 timeobs в UTC, startobs = string (not long!), местное время
            TIME-OBS= '09:00:21.760'
            STARTOBS= '12:55:23.181'
            STOPOBS = '13:05:16.050'
            DSPDT   = 0.007637
            SMOOTH отсутствует, но он равен 30!

            2011, 2012, 2015, 2016 (старая регистрация)
            TIME-OBS = '13:00:28.860'
            STARTOBS = 1318323334
            STOPOBS = 1318323929
            ARMDT   = 0.007000
            SMOOTH  = 30

            2016(новая регистрация), 2017-по настоящее время
            TIME-OBS = 12:15:38.820
            STARTOBS = 1498122824
            ARMDT = 0.200
            SMOOTH = 1
        """

        if metadata.armdt is None:
            dspdt = fits_param_extractor.get_fits_header_value("DSPDT")
            if dspdt is not None and metadata.smooth is None:
                metadata.smooth = 30
                metadata.armdt = dspdt
            else:
                if metadata.smooth is None:
                    metadata.smooth = 1
                    metadata.armdt = 0.210

        metadata.adc_rate = metadata.armdt * metadata.smooth

        # if self._start_obs != 0:
        metadata.datetime_reg_start_local = datetime.fromtimestamp(metadata.start_obs)
        metadata.datetime_culmination_local = datetime.fromtimestamp(
            (metadata.start_obs + (metadata.naxis1 - metadata.crpix1) * metadata.adc_rate))
        metadata.datetime_reg_stop_local = datetime.fromtimestamp(metadata.stop_obs)

        metadata.datetime_reg_start_utc = metadata.datetime_reg_start_local.astimezone(timezone.utc)
        metadata.datetime_culmination_utc = metadata.datetime_culmination_local.astimezone(timezone.utc)
        metadata.datetime_reg_stop_utc = metadata.datetime_reg_stop_local.astimezone(timezone.utc)

        # hdu2 table
        if hdu2_table is None:
            raise RuntimeError(f"HDU2_table is None")

        metadata.hdu2_table = copy.deepcopy(hdu2_table)
        axes = [Axis.FREQUENCY, Axis.POLARIZATION, Axis.SAMPLE]

        fits_table_param_extractor = FitsTableParametersExtractor(hdu2_table)
        frequency_axis = fits_table_param_extractor.get_array("freq")

        sspc_16_start_date = DateUtils.parse_date(SSPC_16_START_DATE, "%Y%m%d")
        if metadata.datetime_culmination_utc > sspc_16_start_date:
            metadata.frequencies = set(frequency_axis[:80])
            metadata.frequencies_wideband = set(frequency_axis[81:])
            polarization_axis = [PolarizationType.RHCP, PolarizationType.LHCP]
        else:
            metadata.frequencies = set(frequency_axis)
            metadata.frequencies_wideband = None
            polarization_axis = [PolarizationType.LHCP, PolarizationType.RHCP]

        metadata.polarizations = copy.deepcopy(polarization_axis)
        metadata.data_layout = DataLayout(axes, frequency_axis, polarization_axis)

        return metadata

    @staticmethod
    def _get_data_dimensions(data: np.array):
        if isinstance(data, np.ndarray) and data.ndim == 3:
            dim1, dim2, dim3 = data.shape
            return dim1, dim2, dim3
        else:
            message = "The data is incorrectly sized: " + str(data.shape) + ". Expected 3D array"
            logger.error(message)
            raise ValueError(message)

