import copy
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

from ratan_600_data_analyzer.logger.logger import logger
from ratan_600_data_analyzer.ratan.axis import Axis
from ratan_600_data_analyzer.ratan.data_layout import DataLayout
from ratan_600_data_analyzer.ratan.data_receiver import DataReceiver
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.desc_reader import DescReader
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_constants import \
    FREQ_MIN, FREQ_MAX
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_metadata import \
    FastAcquisition1To3GHzMetadata
from ratan_600_data_analyzer.ratan.polarization_type import PolarizationType
from ratan_600_data_analyzer.ratan.ratan_metadata_loader import RatanMetadataLoader
from ratan_600_data_analyzer.utils.file_utils import FileUtils


class FastAcquisition1To3GHzMetadataBinLoader(RatanMetadataLoader):

    @staticmethod
    def load(desc_file: Path, bin_file: Path, array_3d: np.ndarray) -> FastAcquisition1To3GHzMetadata:

        metadata = FastAcquisition1To3GHzMetadata()

        try:
            FileUtils.validate_file(bin_file)
        except Exception as e:
            logger.exception(e)
            raise

        if bin_file.suffix == ".bin":
            metadata.data_file_extension = bin_file.suffix
        else:
            raise ValueError(f"File {bin_file} has invalid extension. Expected .bin, but found {bin_file.suffix}")

        metadata.bin_file = bin_file

        metadata.desc_file = bin_file.with_suffix(".desc")
        try:
            FileUtils.validate_file(desc_file)
        except Exception as e:
            logger.exception(e)
            raise ValueError(f"File {metadata.desc_file} has invalid extension. Expected .bin, but found {metadata.desc_file.suffix}")

        metadata.data_receiver = DataReceiver.FAST_ACQUISITION_1_3GHZ

        desc_reader = DescReader()
        desc_data = desc_reader.read(metadata.desc_file)

        metadata.observation_object = desc_data.get_value("fits_words.OBJECT")
        azimuth_str = desc_data.get_value("fits_words.AZIMUTH")
        try:
            metadata.azimuth = float(azimuth_str)
        except ValueError as e:
            message = f"Can't parse string {azimuth_str} to float: {e}"
            logger.exception(f"{message}")
            raise ValueError(f"{message}: {e}") from e

        culmination_str = desc_data.get_value("fits_words.T_OBS")
        metadata.datetime_culmination_local = datetime.fromisoformat(culmination_str)
        metadata.datetime_culmination_utc = metadata.datetime_culmination_local.astimezone(ZoneInfo('UTC'))

        start_time_str = desc_data.get_value("start_time")

        metadata.datetime_reg_start_local = datetime.fromisoformat(start_time_str)
        metadata.datetime_reg_start_utc = metadata.datetime_reg_start_local.astimezone(ZoneInfo('UTC'))

        metadata.solar_p = float(desc_data.get_value("fits_words.SOLAR_P"))
        metadata.solar_b = float(desc_data.get_value("fits_words.SOLAR_B"))
        metadata.solar_r = float(desc_data.get_value("fits_words.SOLAR_R"))

        metadata.altitude = float(desc_data.get_value("fits_words.ALTITUDE"))

        metadata.solar_declination = float(desc_data.get_value("fits_words.DEC"))
        metadata.solar_ra = float(desc_data.get_value("fits_words.RA"))

        metadata.telescope = "RATAN-600"

        if array_3d.ndim == 3:
            num_frequencies = array_3d.shape[0]
            # num_polarizations = data.shape[1]
            samples = array_3d.shape[2]
            axes = [Axis.FREQUENCY, Axis.POLARIZATION, Axis.SAMPLE]
            frequency_axis = np.linspace(FREQ_MIN / 1000, FREQ_MAX / 1000, num=num_frequencies, dtype=np.float64)
            polarization_axis = [PolarizationType.LHCP, PolarizationType.RHCP]

            metadata.data_layout = DataLayout(axes, frequency_axis, polarization_axis)

            metadata.frequencies = copy.deepcopy(frequency_axis)
            metadata.polarizations = copy.deepcopy(polarization_axis)
            metadata.samples = samples

        return metadata