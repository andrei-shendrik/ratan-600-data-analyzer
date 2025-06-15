import logging
import os

from ratan_600_data_analyzer.logger.logger_config import LOG_PATH, LOG_LEVEL, CONSOLE_LEVEL


def setup_logger(path_log, log_level, console_level):

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Минимальный уровень для логгера (пропускаем все)

    # Обработчик для error.log
    error_log_file = os.path.join(LOG_PATH, 'error.log')
    error_file_handler = logging.FileHandler(error_log_file)
    error_file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    error_file_handler.setFormatter(formatter)
    logger.addHandler(error_file_handler)

    # Обработчик для debug.log
    debug_log_file = os.path.join(LOG_PATH, 'debug.log')
    debug_file_handler = logging.FileHandler(debug_log_file)
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(formatter)
    logger.addHandler(debug_file_handler)

    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger(LOG_PATH, LOG_LEVEL, CONSOLE_LEVEL)

#отключение логирования
#logger = None
