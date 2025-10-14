from dataclasses import dataclass, field, InitVar
from pathlib import Path

@dataclass(frozen=True)
class LoggingSettings:

    _log_level: str = field(init=False, repr=False)
    _log_path: Path = field(init=False, repr=False)
    _console_output: bool = field(init=False, repr=False)
    _log_format: str = field(init=False, repr=False)
    _date_format: str = field(init=False, repr=False)
    _failed_bin_files_log: Path = field(init=False, repr=False)
    _debug_log_filename: str = field(init=False, repr=False)
    _info_log_filename: str = field(init=False, repr=False)
    _warning_log_filename: str = field(init=False, repr=False)
    _error_log_filename: str = field(init=False, repr=False)
    _critical_log_filename: str = field(init=False, repr=False)

    log_level: InitVar[str]
    log_path: InitVar[Path]
    console_output: InitVar[bool]
    log_format: InitVar[str]
    date_format: InitVar[str]
    failed_bin_files_log: InitVar[Path]
    debug_log_filename: InitVar[str]
    info_log_filename: InitVar[str]
    warning_log_filename: InitVar[str]
    error_log_filename: InitVar[str]
    critical_log_filename: InitVar[str]

    def __post_init__(
            self,
            log_level,
            log_path,
            console_output,
            log_format,
            date_format,
            failed_bin_files_log,
            debug_log_filename,
            info_log_filename,
            warning_log_filename,
            error_log_filename,
            critical_log_filename
    ):
        object.__setattr__(self, '_log_level', log_level)
        object.__setattr__(self, '_log_path', log_path)
        object.__setattr__(self, '_console_output', console_output)
        object.__setattr__(self, '_log_format', log_format)
        object.__setattr__(self, '_date_format', date_format)
        object.__setattr__(self, '_failed_bin_files_log', failed_bin_files_log)
        object.__setattr__(self, '_debug_log_filename', debug_log_filename)
        object.__setattr__(self, '_info_log_filename', info_log_filename)
        object.__setattr__(self, '_warning_log_filename', warning_log_filename)
        object.__setattr__(self, '_error_log_filename', error_log_filename)
        object.__setattr__(self, '_critical_log_filename', critical_log_filename)

    @property
    def log_level(self) -> str:
        return self._log_level

    @property
    def log_path(self) -> Path:
        return self._log_path

    @property
    def console_output(self) -> bool:
        return self._console_output

    @property
    def log_format(self) -> str:
        return self._log_format

    @property
    def date_format(self) -> str:
        return self._date_format

    @property
    def failed_bin_files_log(self) -> Path:
        return self._failed_bin_files_log

    @property
    def debug_log_filename(self) -> str:
        return self._debug_log_filename

    @property
    def info_log_filename(self) -> str:
        return self._info_log_filename

    @property
    def warning_log_filename(self) -> str:
        return self._warning_log_filename

    @property
    def error_log_filename(self) -> str:
        return self._error_log_filename

    @property
    def critical_log_filename(self) -> str:
        return self._critical_log_filename
