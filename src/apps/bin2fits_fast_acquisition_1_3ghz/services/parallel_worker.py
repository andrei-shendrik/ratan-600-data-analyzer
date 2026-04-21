import logging
import signal
from dataclasses import dataclass
from pathlib import Path
import time
import psutil

from apps.bin2fits_fast_acquisition_1_3ghz.services.observation_processor import \
    FastAcquisition1To3GHzObservationProcessor
from ratan_600_data_analyzer.logging.logger_configurator import LoggerConfigurator

# требование памяти для одного процесса
REQUIRED_RAM_GB = 2.0

def init_worker():
    """
    Вызывается при старте каждого дочернего процесса в пуле.
    Приказывает воркеру ИГНОРИРОВАТЬ сигнал Ctrl+C.
    Это позволяет воркеру спокойно доделать текущий файл,
    пока главный процесс управляет мягкой остановкой пула.
    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)

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

    # требование свободной памяти
    while True:
        available_ram_gb = psutil.virtual_memory().available / (1024 ** 3)
        if available_ram_gb > REQUIRED_RAM_GB:
            break
        logger.warning(f"[{filename}] Low Memory ({available_ram_gb:.1f}GB < {REQUIRED_RAM_GB}GB). Waiting...")
        print(f"\r[THROTTLE] {filename} is waiting for RAM... (Free: {available_ram_gb:.1f} GB)", end="", flush=True)
        time.sleep(5)  # Спим 5 секунд и проверяем снова

    print("\r" + " " * 80 + "\r", end="", flush=True)
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