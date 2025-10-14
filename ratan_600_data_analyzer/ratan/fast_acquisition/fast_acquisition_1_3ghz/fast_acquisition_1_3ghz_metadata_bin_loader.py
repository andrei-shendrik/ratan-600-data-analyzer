import copy
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import astropy
import sunpy.coordinates.sun
import numpy as np
import astropy.units as u
from astropy.coordinates import get_sun, SkyCoord, AltAz, EarthLocation
from astropy.time import Time

from ratan_600_data_analyzer.logger.logger import logger
from ratan_600_data_analyzer.ratan.coordinate_axes import CoordinateAxes
from ratan_600_data_analyzer.ratan.data_receiver import DataReceiver
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.desc_reader import DescReader
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_configuration import \
    config
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_data import \
    FastAcquisition1To3GHzData
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_metadata import \
    FastAcquisition1To3GHzMetadata
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.raw_data.fast_acquisition_1_3ghz_raw_data import \
    FastAcquisition1To3GHzRawData
from ratan_600_data_analyzer.ratan.polarization_type import PolarizationType
from ratan_600_data_analyzer.ratan.ratan_metadata_loader import RatanMetadataLoader
from ratan_600_data_analyzer.utils.file_utils import FileUtils


class FastAcquisition1To3GHzMetadataBinLoader(RatanMetadataLoader):

    @staticmethod
    def load(bin_file: Path, fast_acq_data: FastAcquisition1To3GHzData,
             fast_acq_raw_data: FastAcquisition1To3GHzRawData) -> FastAcquisition1To3GHzMetadata:

        metadata = FastAcquisition1To3GHzMetadata()

        try:
            FileUtils.validate_file(bin_file)
        except Exception as e:
            logger.exception(e)
            raise

        bin_file_extensions = bin_file.suffixes
        bin_file_name = bin_file.name
        full_extension = "".join(bin_file.suffixes)
        bin_file_base_name = bin_file_name.removesuffix(full_extension)

        if bin_file_extensions == ['.bin', '.gz']:
            metadata.data_file_extension = ".bin.gz"
        elif bin_file_extensions == ['.bin']:
            metadata.data_file_extension = ".bin"
        else:
            raise ValueError(f"File {bin_file} has invalid extension. Expected .bin, but found {bin_file.suffix}")

        metadata.bin_file = bin_file
        metadata.desc_file = bin_file.with_name(bin_file_base_name + ".desc")
        try:
            FileUtils.validate_file(metadata.desc_file)
        except Exception as e:
            logger.exception(e)
            raise ValueError(f"File {metadata.desc_file} has invalid extension. Expected .desc, but found {metadata.desc_file.suffix}")

        metadata.data_receiver = DataReceiver.FAST_ACQUISITION_1_3GHZ

        desc_reader = DescReader()
        desc_data = desc_reader.read(metadata.desc_file)

        metadata.telescope = "RATAN-600"
        metadata.observation_object = desc_data.get_value("object")
        azimuth_str = desc_data.get_value("azimuth")
        try:
            metadata.azimuth = float(azimuth_str)
        except ValueError as e:
            message = f"Can't parse string {azimuth_str} to float: {e}"
            logger.exception(f"{message}")
            raise ValueError(f"{message}: {e}") from e

        culmination_str = desc_data.get_value("culmination") #("fits_words.T_OBS")
        metadata.datetime_culmination_efrat_local = datetime.fromisoformat(culmination_str)
        metadata.datetime_culmination_efrat_utc = metadata.datetime_culmination_efrat_local.astimezone(ZoneInfo('UTC'))

        #start_time_str = desc_data.get_value("start_time")

        metadata.attenuator_common = desc_data.get_value("acquisition_parameters.attenuator_common")
        metadata.attenuator_1_2ghz = desc_data.get_value("acquisition_parameters.attenuator_12ghz")
        metadata.attenuator_2_3ghz = desc_data.get_value("acquisition_parameters.attenuator_23ghz")

        kurtosis_lower_bound_1_2ghz = desc_data.get_value("acquisition_parameters.kurtosis_lower_bound_12ghz")
        kurtosis_upper_bound_1_2ghz = desc_data.get_value("acquisition_parameters.kurtosis_upper_bound_12ghz")
        kurtosis_lower_bound_2_3ghz = desc_data.get_value("acquisition_parameters.kurtosis_lower_bound_23ghz")
        kurtosis_upper_bound_2_3ghz = desc_data.get_value("acquisition_parameters.kurtosis_upper_bound_23ghz")
        if (abs(kurtosis_lower_bound_1_2ghz) ==
                abs(kurtosis_upper_bound_1_2ghz) ==
                abs(kurtosis_lower_bound_2_3ghz) ==
                abs(kurtosis_upper_bound_2_3ghz)):
            metadata.half_width_kurtosis_interval = abs(kurtosis_lower_bound_1_2ghz)

        metadata.samples_per_second = config.samples_per_second
        """
            использован код Михаила
        """
        observing_time = Time(metadata.datetime_culmination_efrat_utc)
        observing_time_delay = config.obs_time_delay

        ra0, dec0 = sunpy.coordinates.sun.sky_position(observing_time)
        metadata.right_ascension = astropy.coordinates.Angle(ra0, unit=u.deg)
        metadata.declination = astropy.coordinates.Angle(dec0, unit=u.deg)

        metadata.solar_r = sunpy.coordinates.sun.angular_radius(observing_time)
        metadata.solar_p = sunpy.coordinates.sun.P(observing_time)
        metadata.solar_b = sunpy.coordinates.sun.B0(observing_time)

        # metadata.altitude = float(desc_data.get_value("fits_words.ALTITUDE")) # no keyword
        # metadata.solar_p = float(desc_data.get_value("fits_words.SOLAR_P"))
        # metadata.solar_b = float(desc_data.get_value("fits_words.SOLAR_B"))
        # metadata.solar_r = float(desc_data.get_value("fits_words.SOLAR_R"))
        # metadata.solar_declination = float(desc_data.get_value("fits_words.DEC"))
        # metadata.solar_ra = float(desc_data.get_value("fits_words.RA"))

        solar_coords = SkyCoord(ra0, dec0, frame='icrs')
        solar_altaz = solar_coords.transform_to(AltAz(obstime=observing_time, location=config.ratan_location))

        new_altaz = SkyCoord(AltAz(obstime=observing_time + observing_time_delay * u.s,
                                   az=solar_altaz.az,
                                   alt=solar_altaz.alt,
                                   location=config.ratan_location),)
        new_radec = new_altaz.transform_to('icrs')
        ra1, dec1 = new_radec.ra, new_radec.dec

        lst = observing_time.sidereal_time("mean", longitude=config.ratan_location.lon)
        ha = lst - ra0
        metadata.solar_position_angle = astropy.coordinates.Angle(np.arctan(np.sin(dec0) * np.tan(ha)), unit=u.deg)
        metadata.arcsec_per_second = ((np.arccos(np.cos(ra0) * np.cos(dec0) * np.cos(ra1) * np.cos(dec1)
                                             + np.sin(ra0) * np.cos(dec0) * np.sin(ra1) * np.cos(dec1)
                                             + np.sin(dec0) * np.sin(dec1)) / u.rad)
                                  / np.pi * 180 * 60 * 60 / observing_time_delay)

        # Прочитать pulse1_rlc и pulse2_rlc. Найти сэмплы с началом последнего импульса и концом препоследнего.
        # Проверить, похоже ли время на правду
        # Можно ли верить Трушкину по поводу feed_offset_time?
        metadata.feed_offset = float(desc_data.get_value("feed_offset"))
        metadata.feed_offset_time = timedelta(seconds=float(desc_data.get_value("feed_offset_time")))
        metadata.start_pulse_edge_time = int(desc_data.get_value("pulse1_rlc")[1])
        metadata.stop_pulse_edge_time = int(desc_data.get_value("pulse2_rlc")[0])

        FastAcquisition1To3GHzMetadataBinLoader.find_pulse_edge_samples(metadata, fast_acq_raw_data)

        metadata.datetime_culmination_feed_horn_utc = metadata.datetime_culmination_efrat_utc + metadata.feed_offset_time
        metadata.datetime_culmination_feed_horn_local = metadata.datetime_culmination_efrat_local + metadata.feed_offset_time

        time_between_pulse_edges = metadata.stop_pulse_edge_time - metadata.start_pulse_edge_time
        samples_between_pulse_edges = metadata.stop_pulse_edge_sample - metadata.start_pulse_edge_sample
        # if np.abs(samples_between_pulse_edges / metadata.time_reduction_factor
        #           - time_between_pulse_edges * SAMPLES_PER_SECOND / metadata.time_reduction_factor) > 5:
            #logging.warning(f"read_description(): probably something is wrong with calibration pulse timing")

        # Найти сэмпл - середину Солнца ("локальную кульминацию"). *_arcsec_scale сместить так,
        # чтобы этот сэмпл приходился на ее начало.
        metadata.ref_time = (metadata.start_pulse_edge_sample / config.samples_per_second - metadata.start_pulse_edge_time)
        metadata.ref_sample = metadata.start_pulse_edge_sample - metadata.start_pulse_edge_time * config.samples_per_second
        metadata.arcsec_per_sample = metadata.arcsec_per_second / config.samples_per_second

        lhcp = fast_acq_data.lhcp
        rhcp = fast_acq_data.rhcp
        if lhcp.shape != rhcp.shape:
            metadata.is_bad = True
            raise ValueError(f"Polarization arrays has different sizes: {lhcp.shape} != {rhcp.shape}. Observation marked as bad.")
        num_frequencies = lhcp.shape[0]
        num_samples = lhcp.shape[1]

        frequency_axis = np.linspace(config.freq_min / 1000, config.freq_max / 1000, num=num_frequencies, dtype=np.float64)
        polarization_axis = [PolarizationType.LHCP, PolarizationType.RHCP]

        metadata.frequencies = copy.deepcopy(frequency_axis)
        metadata.polarizations = copy.deepcopy(polarization_axis)
        metadata.num_frequencies = num_frequencies
        metadata.num_samples = num_samples

        metadata.datetime_reg_start_utc = metadata.datetime_culmination_feed_horn_utc - timedelta(
            seconds=metadata.ref_time)
        metadata.datetime_reg_start_local = metadata.datetime_reg_start_utc.astimezone(timezone(timedelta(hours=3)))

        metadata.record_duration_seconds = metadata.num_samples / config.samples_per_second

        metadata.datetime_reg_stop_utc = metadata.datetime_reg_start_utc + timedelta(
            seconds=metadata.record_duration_seconds)
        metadata.datetime_reg_stop_local = metadata.datetime_reg_start_local + timedelta(
            seconds=metadata.record_duration_seconds)

        frequency_axis = np.linspace(config.freq_min, config.freq_max, num_frequencies)
        time_axis = np.arange(num_samples) / config.samples_per_second
        arcsec_axis = - (time_axis - metadata.ref_time) * metadata.arcsec_per_second

        coordinate_axes = CoordinateAxes()
        coordinate_axes.frequency_axis = frequency_axis
        coordinate_axes.time_axis = time_axis
        coordinate_axes.arcsec_axis = arcsec_axis
        metadata.coordinate_axes = coordinate_axes

        metadata.time_reduction_factor = 1
        metadata.frequency_resolution = (config.freq_max - config.freq_min) / frequency_axis.size
        metadata.time_resolution = 1 / config.samples_per_second
        metadata.arcsec_resolution = 1 / metadata.arcsec_per_second
        metadata.switch_polarization_time = 1 / config.switch_polarization_frequency # sec

        return metadata

    @staticmethod
    def find_pulse_edge_samples(metadata: FastAcquisition1To3GHzMetadata, fast_acq_raw_data: FastAcquisition1To3GHzRawData):

        ch0_pol0_state = fast_acq_raw_data.generator_state_data.c0p0_state
        ch1_pol0_state = fast_acq_raw_data.generator_state_data.c1p0_state

        ch0_pol1_state = fast_acq_raw_data.generator_state_data.c0p1_state
        ch1_pol1_state = fast_acq_raw_data.generator_state_data.c1p1_state

        pol0_generator_state = (
                (np.hstack((np.fliplr(ch0_pol0_state), ch1_pol0_state)).T & 2 ** config.generator_bit) >> config.generator_bit
        )
        if pol0_generator_state.shape[1] == 0:
            pol0_generator_state = None

        pol1_generator_state = (
                (np.hstack((np.fliplr(ch0_pol1_state), ch1_pol1_state)).T & 2 ** config.generator_bit) >> config.generator_bit
        )
        if pol1_generator_state.shape[1] == 0:
            pol1_generator_state = None

        pol0_edge_h = -1
        pol0_edge_l = sys.maxsize
        pol1_edge_h = -1
        pol1_edge_l = sys.maxsize

        if pol0_generator_state is not None:
            median = pol0_generator_state.shape[1] // 2
            try:
                pol0_edge_h = median + np.nonzero(pol0_generator_state[0, median:])[0][0]
                pol0_edge_l = np.nonzero(pol0_generator_state[0, :median])[-1][-1]
            except IndexError as ex:
                raise ValueError(f"find_pulse_edge_samples(): pol0: probably pulse not found: {ex}")
                #logging.warning(f"find_pulse_edge_samples(): pol0: probably pulse not found: {ex}")
        if pol0_edge_l == sys.maxsize:
            pol0_edge_l = -1
        if pol0_edge_h == -1:
            pol0_edge_h = sys.maxsize

        if pol1_generator_state is not None:
            median = pol1_generator_state.shape[1] // 2
            try:
                pol1_edge_h = median + np.nonzero(pol1_generator_state[0, median:])[0][0]
                pol1_edge_l = np.nonzero(pol1_generator_state[0, :median])[-1][-1]
            except IndexError as ex:
                raise ValueError(f"find_pulse_edge_samples(): pol1: probably pulse not found: {ex}")
                #logging.warning(f"find_pulse_edge_samples(): pol1: probably pulse not found: {ex}")
        if pol1_edge_l == sys.maxsize:
            pol1_edge_l = -1
        if pol1_edge_h == -1:
            pol1_edge_h = sys.maxsize

        edge_l = max(pol0_edge_l, pol1_edge_l)
        edge_h = min(pol0_edge_h, pol1_edge_h)

        if edge_l != sys.maxsize:
            metadata.start_pulse_edge_sample = edge_l
        if edge_h != -1:
            metadata.stop_pulse_edge_sample = edge_h