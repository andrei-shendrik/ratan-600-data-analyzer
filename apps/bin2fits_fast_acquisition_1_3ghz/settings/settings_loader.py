import tomllib
from pathlib import Path

from apps.bin2fits_fast_acquisition_1_3ghz.settings.bin2fits_fast_acquisition_1_3ghz_settings import \
    BinToFitsFastAcquisition1To3GHzSettings
from apps.bin2fits_fast_acquisition_1_3ghz.logging.logging_settings import LoggingSettings


class SettingsLoader:

    def __init__(self, config_file: Path):
        self._config_file = config_file
        if not self._config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self._config_file}")

    def load(self) -> BinToFitsFastAcquisition1To3GHzSettings:
        try:
            with open(self._config_file, 'rb') as f:
                toml_content = tomllib.load(f)

            logging_section = toml_content.get('logging', {})

            handler_filenames = {}
            handlers_list = logging_section.get('handlers', [])
            for handler_config in handlers_list:
                level = handler_config.get('level', '').upper()
                filename = handler_config.get('filename')
                if not filename:
                    continue
                if level == 'DEBUG':
                    handler_filenames['debug_log_filename'] = filename
                elif level == 'INFO':
                    handler_filenames['info_log_filename'] = filename
                elif level == 'WARNING':
                    handler_filenames['warning_log_filename'] = filename
                elif level == 'ERROR':
                    handler_filenames['error_log_filename'] = filename
                elif level == 'CRITICAL':
                    handler_filenames['critical_log_filename'] = filename

            logging_settings = LoggingSettings(
                log_level=logging_section['log_level'],
                log_path=Path(logging_section['log_path']),
                console_output=logging_section.get('console_output', True),
                log_format=logging_section['log_format'],
                date_format=logging_section['date_format'],
                failed_bin_files_log=Path(logging_section['failed_bin_files_log']),
                debug_log_filename=handler_filenames['debug_log_filename'],
                info_log_filename=handler_filenames['info_log_filename'],
                warning_log_filename=handler_filenames['warning_log_filename'],
                error_log_filename=handler_filenames['error_log_filename'],
                critical_log_filename=handler_filenames['critical_log_filename']
            )

            paths_section = toml_content.get('paths', {})

            return BinToFitsFastAcquisition1To3GHzSettings(
                bin_archive=Path(paths_section['bin_archive']),
                fits_archive=Path(paths_section['fits_archive']),
                logging=logging_settings
            )

        except KeyError as e:
            raise RuntimeError(f"Missing required key '{e.args[0]}' in configuration file: {self._config_file}")
        except Exception as e:
            raise RuntimeError(f"Error loading configuration: {e}") from e
