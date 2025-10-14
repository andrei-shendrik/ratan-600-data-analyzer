from dataclasses import dataclass, field, InitVar
from pathlib import Path

from apps.bin2fits_fast_acquisition_1_3ghz.logging.logging_settings import LoggingSettings

@dataclass(frozen=True)
class BinToFitsFastAcquisition1To3GHzSettings:
    _bin_archive: Path = field(init=False, repr=False)
    _fits_archive: Path = field(init=False, repr=False)
    _logging: LoggingSettings = field(init=False, repr=False)

    bin_archive: InitVar[Path]
    fits_archive: InitVar[Path]
    logging: InitVar[LoggingSettings]

    @property
    def bin_archive(self) -> Path:
        return self._bin_archive

    @property
    def fits_archive(self) -> Path:
        return self._fits_archive

    @property
    def logging(self) -> LoggingSettings:
        return self._logging

    def __post_init__(
            self,
            bin_archive: Path,
            fits_archive: Path,
            logging: LoggingSettings,
    ):
        object.__setattr__(self, '_bin_archive', bin_archive)
        object.__setattr__(self, '_fits_archive', fits_archive)
        object.__setattr__(self, '_logging', logging)