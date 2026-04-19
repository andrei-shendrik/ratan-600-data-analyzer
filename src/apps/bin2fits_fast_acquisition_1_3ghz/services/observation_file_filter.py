import logging
import re
from pathlib import Path

from apps.bin2fits_fast_acquisition_1_3ghz.settings.bin2fits_fast_acquisition_1_3ghz_settings import FileFilterSettings

logger = logging.getLogger(__name__)

class ObservationFileFilter:
    """
        Фильтрация наблюдений по имени файла: брать в обработку или нет
    """
    def __init__(self, settings: 'FileFilterSettings'):
        self._allowed_patterns = [re.compile(p) for p in settings.allowed_patterns]
        self._forbidden_patterns = [re.compile(p) for p in settings.forbidden_patterns]

    def is_valid(self, file_path: Path) -> bool:
        filename = file_path.name

        if not (filename.endswith('.bin') or filename.endswith('.bin.gz')):
            return False

        for pattern in self._forbidden_patterns:
            if pattern.search(filename):
                logger.debug(f"[{filename}] Filtered out: matches forbidden pattern '{pattern.pattern}'")
                return False

        for pattern in self._allowed_patterns:
            if pattern.match(filename):
                return True

        logger.debug(f"[{filename}] Filtered out: does not match any allowed pattern.")
        return False