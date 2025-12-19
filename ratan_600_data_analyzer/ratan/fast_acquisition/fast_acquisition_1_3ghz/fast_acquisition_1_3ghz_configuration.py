import tomllib
from importlib.resources import files
from pathlib import Path

import astropy
import numpy as np
from astropy.coordinates import Angle, EarthLocation
import astropy.units as u

from ratan_600_data_analyzer.common.project_info import ProjectInfo


class FastAcquisition1To3GHzConfiguration:
    def __init__(self):

        self._pol_ch0 = None
        self._pol_ch1 = None

        self._chunk_length = None
        self._polarization_mask = None
        self._dt = None
        self._samples_per_second = None

        self._kurt_threshold = None
        self._generator_bit = None
        self._switch_polarization_frequency = None

        self._freq_min = None
        self._freq_max = None

        self._obs_time_delay = None

        self._ratan_location = None

        self._arcsec_min = None
        self._arcsec_max = None

        self._raw_missing_value_replacement = None
        self._raw_kurtosis_value_replacement = None
        self._calibr_missing_value_replacement = None
        self._calibr_kurtosis_value_replacement = None

        self._filter_bands = None

        self._flux_dm_file = None

    @classmethod
    def load(cls, config_file: Path) -> 'FastAcquisition1To3GHzConfiguration':

        instance = cls()
        try:
            with open(config_file, "rb") as f:
                config_data = tomllib.load(f)
                channels = config_data['channels']
                instance._pol_ch0 = channels['pol_ch0']
                instance._pol_ch1 = channels['pol_ch1']

                bin_data = config_data['bin_data']
                instance._chunk_length = bin_data['chunk_length']
                instance._polarization_mask = bin_data['polarization_mask']
                instance._dt = np.dtype([tuple(field) for field in bin_data['dt']])

                adc = config_data['adc']
                instance._samples_per_second = adc['clock'] / adc['factor1'] / adc['factor2']
                instance._kurt_threshold = adc['kurt_threshold']
                instance._generator_bit = adc['generator_bit']
                instance._switch_polarization_frequency = adc['switch_polarization_frequency']
                instance._freq_min = adc['freq_min']
                instance._freq_max = adc['freq_max']
                instance._obs_time_delay = adc['obs_time_delay']

                ratan = config_data['ratan']
                lat_data = ratan['latitude']
                lon_data = ratan['longitude']
                lat_str = f"{lat_data['d']}d{lat_data['m']}m{lat_data['s']}s"
                lon_str = f"{lon_data['d']}d{lon_data['m']}m{lon_data['s']}s"
                lat = astropy.coordinates.Angle(lat_str, unit=ratan['latitude']['unit'])
                lon = astropy.coordinates.Angle(lon_str, unit=ratan['longitude']['unit'])
                height = ratan['height']['value'] * u.Unit(ratan['height']['unit'])
                instance._ratan_location = EarthLocation(lat=lat, lon=lon, height=height)

                calibr = config_data['calibration']
                relative_path = calibr['flux_dm_file']
                instance._flux_dm_file = files('ratan_600_data_analyzer').joinpath(relative_path)
                instance._arcsec_min = calibr['arcsec_min']
                instance._arcsec_max = calibr['arcsec_max']

                value_replacement = config_data['value_replacement']
                instance._raw_missing_value_replacement = value_replacement['raw_missing_value_replacement']
                instance._raw_kurtosis_value_replacement = value_replacement['raw_kurtosis_value_replacement']
                instance._calibr_missing_value_replacement = value_replacement['calibr_missing_value_replacement']
                instance._calibr_kurtosis_value_replacement = value_replacement['calibr_kurtosis_value_replacement']

                filtration = config_data['filtration']
                instance._filter_bands = filtration['filter_bands']
                return instance
        except FileNotFoundError:
            raise RuntimeError(f"Configuration file not found: {config_file}")
        except KeyError as e:
            raise RuntimeError(f"Missing key '{e.args[0]}' in configuration file: {config_file}")
        except Exception as e:
            raise RuntimeError(f"Error: {e}") from e

    @property
    def pol_ch0(self) -> str:
        return self._pol_ch0

    @property
    def pol_ch1(self) -> str:
        return self._pol_ch1

    @property
    def chunk_length(self) -> int:
        return self._chunk_length

    @property
    def polarization_mask(self) -> int:
        return self._polarization_mask

    @property
    def dt(self) -> np.dtype:
        return self._dt

    @property
    def samples_per_second(self) -> float:
        return self._samples_per_second

    @property
    def kurt_threshold(self) -> int:
        return self._kurt_threshold

    @property
    def generator_bit(self) -> int:
        return self._generator_bit

    @property
    def switch_polarization_frequency(self) -> int:
        return self._switch_polarization_frequency

    @property
    def freq_min(self) -> int:
        return self._freq_min

    @property
    def freq_max(self) -> int:
        return self._freq_max

    @property
    def obs_time_delay(self) -> int:
        return self._obs_time_delay

    @property
    def ratan_location(self) -> EarthLocation:
        return self._ratan_location

    @property
    def arcsec_min(self) -> int:
        return self._arcsec_min

    @property
    def arcsec_max(self) -> int:
        return self._arcsec_max

    @property
    def raw_missing_value_replacement(self) -> int:
        return self._raw_missing_value_replacement

    @property
    def raw_kurtosis_value_replacement(self) -> int:
        return self._raw_kurtosis_value_replacement

    @property
    def calibr_missing_value_replacement(self) -> float:
        return self._calibr_missing_value_replacement

    @property
    def calibr_kurtosis_value_replacement(self) -> float:
        return self._calibr_kurtosis_value_replacement

    @property
    def filter_bands(self) -> np.ndarray:
        return self._filter_bands

    @property
    def flux_dm_file(self) -> np.ndarray:
        return self._flux_dm_file

project_root = ProjectInfo.find_project_root()
CONFIG_FILE = project_root / "ratan_600_data_analyzer/ratan/fast_acquisition/fast_acquisition_1_3ghz/config/fast_acquisition_1_3ghz_config.toml"
config = FastAcquisition1To3GHzConfiguration.load(CONFIG_FILE)