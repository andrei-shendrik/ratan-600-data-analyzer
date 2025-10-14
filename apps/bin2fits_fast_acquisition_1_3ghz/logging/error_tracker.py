from pathlib import Path

from apps.bin2fits_fast_acquisition_1_3ghz.settings.bin2fits_fast_acquisition_1_3ghz_settings import \
    BinToFitsFastAcquisition1To3GHzSettings
from apps.bin2fits_fast_acquisition_1_3ghz.logging.logger_configurator import get_logger

logger = get_logger(__name__)

class ErrorTracker:
    def __init__(self, settings: BinToFitsFastAcquisition1To3GHzSettings):
        self._failed_bin_files_log: Path = settings.logging.failed_bin_files_log
        self._failed_files = self._load()

    def _load(self) -> set:
        try:
            with open(self._failed_bin_files_log, 'r') as f:
                return set(line.strip() for line in f if line.strip())
        except FileNotFoundError:
            return set()

    def add(self, file_path: str):
        if file_path not in self._failed_files:
            self._failed_files.add(file_path)
            with open(self._failed_bin_files_log, 'a') as f:
                f.write(f"{file_path}\n")
            logger.warning(f"File {file_path} added to failed list")

    def remove(self, file_path: str):
        if file_path in self._failed_files:
            self._failed_files.remove(file_path)
            self._rewrite_file()
            logger.info(f"File {file_path} removed from failed list")

    def _rewrite_file(self):
        with open(self._failed_bin_files_log, 'w') as f:
            for path in sorted(list(self._failed_files)):
                f.write(f"{path}\n")

    def contains(self, file_path: str) -> bool:
        return file_path in self._failed_files