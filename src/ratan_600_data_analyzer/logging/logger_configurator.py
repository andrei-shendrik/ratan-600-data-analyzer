import copy
import logging

from colorama import Fore, Style

from ratan_600_data_analyzer.logging.logging_settings import LoggingSettings

class LoggerConfigurator:
    def __init__(self, settings: LoggingSettings):
        self._settings = settings

    def configure(self, is_worker: bool = False) -> ListLogHandler | None:
        """
            Настройка логгера.
            Если is_worker=True, настраивает перехват логов в память и возвращает ListLogHandler.
            Иначе настраивает консоль и файлы, возвращает None.
        """
        numeric_log_level = getattr(logging, self._settings.log_level.upper(), logging.INFO)
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_log_level)

        if root_logger.hasHandlers():
            root_logger.handlers.clear()

        # Базовый форматтер (без цвета, для файлов и памяти)
        formatter = logging.Formatter(
            fmt=self._settings.log_format,
            datefmt=self._settings.date_format
        )

        # мультипроцессный режим
        if is_worker:
            list_handler = ListLogHandler()
            list_handler.setLevel(numeric_log_level)
            list_handler.setFormatter(formatter)
            root_logger.addHandler(list_handler)
            return list_handler

        # обычный режим
        if self._settings.console_output:
            console_formatter = ColoredFormatter(
                fmt=self._settings.log_format,
                datefmt=self._settings.date_format
            )
            console_handler = logging.StreamHandler()
            console_handler.setLevel(numeric_log_level)
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)

        for level_name, filename in self._settings.handlers.items():
            level_int = getattr(logging, level_name.upper(), logging.INFO)
            self._add_file_handler(root_logger, level_int, filename, formatter)

        return None

    # def configure(self):
    #     # Получаем базовый уровень логирования (например, из .env)
    #     numeric_log_level = getattr(logging, self._settings.log_level.upper(), logging.INFO)
    #
    #     root_logger = logging.getLogger()
    #     root_logger.setLevel(numeric_log_level)
    #
    #     # Очищаем старые хендлеры, чтобы логи не дублировались при перезапусках
    #     if root_logger.hasHandlers():
    #         root_logger.handlers.clear()
    #
    #     # Базовый форматтер для файлов
    #     formatter = logging.Formatter(
    #         fmt=self._settings.log_format,
    #         datefmt=self._settings.date_format
    #     )
    #
    #     # 1. Настройка вывода в консоль
    #     if self._settings.console_output:
    #         console_formatter = ColoredFormatter(
    #             fmt=self._settings.log_format,
    #             datefmt=self._settings.date_format
    #         )
    #         console_handler = logging.StreamHandler()
    #         console_handler.setLevel(numeric_log_level)
    #         console_handler.setFormatter(console_formatter)
    #         root_logger.addHandler(console_handler)
    #
    #     # 2. Динамическая настройка файлов на основе словаря handlers из TOML
    #     for level_name, filename in self._settings.handlers.items():
    #         # Превращаем строку "DEBUG" в число logging.DEBUG
    #         level_int = getattr(logging, level_name.upper(), logging.INFO)
    #         self._add_file_handler(root_logger, level_int, filename, formatter)
    #
    def _add_file_handler(self, logger: logging.Logger, level: int, filename: str, formatter: logging.Formatter):
        # Используем современный pathlib вместо os.makedirs
        log_folder = self._settings.base_dir
        log_folder.mkdir(parents=True, exist_ok=True)

        full_path = log_folder / filename

        handler = logging.FileHandler(full_path, encoding='utf-8')
        handler.setLevel(level)
        handler.setFormatter(formatter)

        # Фильтр: писать только конкретный уровень (например, в ошибках нет инфо)
        handler.addFilter(lambda record: record.levelno >= level)

        logger.addHandler(handler)


class ListLogHandler(logging.Handler):
    """
        Сохраняет LogRecord в память для передачи между процессами
    """

    def __init__(self):
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record):
        self.format(record)

        record.args = None
        record.exc_info = None
        self.records.append(copy.copy(record))

class ColoredFormatter(logging.Formatter):
    """
        Console colored formatter
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


