import logging
from dataclasses import dataclass
from pathlib import Path

from apps.bin2fits_fast_acquisition_1_3ghz.services.observation_processor import \
    FastAcquisition1To3GHzObservationProcessor
from ratan_600_data_analyzer.logging.logger_configurator import LoggerConfigurator


@dataclass
class WorkerResult:
    """Для параллельного выполнения"""
    filename: str
    success: bool
    error_msg: str
    log_records: list[logging.LogRecord]

def parallel_worker(bin_file: Path, output_fits_file: Path, overwrite: bool, app_settings, file_index: int, total_files: int) -> WorkerResult:
    filename = bin_file.name
    success = False
    error_msg = ""
    captured_logs = []

    # Настройка логгера внутри воркера
    configurator = LoggerConfigurator(app_settings.logging_settings)
    list_handler = configurator.configure(is_worker=True)

    logger = logging.getLogger("worker")

    try:
        # Запуск обработки
        logger.info(f"=== [File {file_index} of {total_files}] === [{filename}] ===")
        FastAcquisition1To3GHzObservationProcessor.execute(bin_file, output_fits_file, overwrite)
        success = True
    except Exception as e:
        error_msg = str(e)[:500]
        logger.error(f"[{filename}] Fatal Pipeline Error: {error_msg}", exc_info=True)
    finally:
        if list_handler:
            captured_logs = list_handler.records

    return WorkerResult(filename, success, error_msg, captured_logs)