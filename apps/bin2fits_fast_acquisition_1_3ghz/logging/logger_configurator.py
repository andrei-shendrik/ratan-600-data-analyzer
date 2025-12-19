import logging
import os

from colorama import Fore, Style

from apps.bin2fits_fast_acquisition_1_3ghz.logging.logging_settings import LoggingSettings


class LoggerConfigurator:
    def __init__(self, settings: LoggingSettings):
        self._settings = settings

    def configure(self):
        numeric_log_level = getattr(logging, self._settings.log_level, logging.INFO)
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_log_level)

        if root_logger.hasHandlers():
            root_logger.handlers.clear()

        formatter = logging.Formatter(
            fmt=self._settings.log_format,
            datefmt=self._settings.date_format
        )

        console_formatter = ColoredFormatter(
            fmt=self._settings.log_format,
            datefmt=self._settings.date_format
        )

        if self._settings.console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(numeric_log_level)
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)

        # if self._settings.console_output:
        #     console_handler = logging.StreamHandler()
        #     console_handler.setLevel(numeric_log_level)
        #     console_handler.setFormatter(formatter)
        #     root_logger.addHandler(console_handler)

        self._add_file_handler(root_logger, logging.DEBUG, self._settings.debug_log_filename, formatter)
        self._add_file_handler(root_logger, logging.INFO, self._settings.info_log_filename, formatter)
        self._add_file_handler(root_logger, logging.WARNING, self._settings.warning_log_filename, formatter)
        self._add_file_handler(root_logger, logging.ERROR, self._settings.error_log_filename, formatter)
        self._add_file_handler(root_logger, logging.CRITICAL, self._settings.critical_log_filename, formatter)

    def _add_file_handler(self, logger: logging.Logger, level: int, filename: str, formatter: logging.Formatter):
        log_folder = self._settings.log_path
        os.makedirs(log_folder, exist_ok=True)
        full_path = log_folder / filename
        handler = logging.FileHandler(full_path, encoding='utf-8')
        handler.setLevel(level)
        handler.setFormatter(formatter)
        handler.addFilter(lambda record: record.levelno == level)
        logger.addHandler(handler)


class ColoredFormatter(logging.Formatter):

    """
        console colored formatter
    """

    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, Fore.RESET)
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


