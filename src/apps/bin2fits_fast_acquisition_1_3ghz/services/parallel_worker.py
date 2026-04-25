import logging
import signal
import sys
from dataclasses import dataclass
from pathlib import Path
import time
import psutil

from apps.bin2fits_fast_acquisition_1_3ghz.services.process_profiler import ProcessProfiler

if sys.platform != 'win32':
    import resource

from apps.bin2fits_fast_acquisition_1_3ghz.services.observation_processor import \
    FastAcquisition1To3GHzObservationProcessor
from ratan_600_data_analyzer.logging.logger_configurator import LoggerConfigurator

def init_worker(worker_max_ram_gb: float):
    """
    Вызывается при старте каждого дочернего процесса в пуле.
    Приказывает воркеру ИГНОРИРОВАТЬ сигнал Ctrl+C.
    Это позволяет воркеру спокойно доделать текущий файл,
    пока главный процесс управляет мягкой остановкой пула.
    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    # Модуль resource доступен только в UNIX/Linux
    if sys.platform != 'win32':
        bytes_limit = int(worker_max_ram_gb * 1024 * 1024 * 1024)

        try:
            # RLIMIT_AS (Address Space) - общий объем виртуальной памяти процесса
            resource.setrlimit(resource.RLIMIT_AS, (bytes_limit, bytes_limit))
        except ValueError:
            # Выбрасывается, если пытаемся поднять лимит выше разрешенного ОС
            pass

@dataclass
class WorkerResult:
    """Для параллельного выполнения"""
    filename: str
    success: bool
    error_msg: str
    log_records: list[logging.LogRecord]

    execution_time_seconds: float
    peak_memory_mb: float

def parallel_worker(bin_file: Path, output_fits_file: Path, overwrite: bool, app_settings, file_index: int, total_files: int) -> WorkerResult:

    filename = bin_file.name
    success = False
    error_msg = ""
    captured_logs = []

    exec_time = 0.0
    peak_ram = 0.0

    min_required_ram = app_settings.resources.min_free_ram_gb
    max_worker_ram = app_settings.resources.worker_max_ram_gb

    # Настройка логгера внутри воркера
    configurator = LoggerConfigurator(app_settings.logging_settings)
    list_handler = configurator.configure(is_worker=True)

    logger = logging.getLogger("worker")

    # 1. ожидание свободных ресурсов
    try:
        while True:
            available_ram_gb = psutil.virtual_memory().available / (1024 ** 3)
            if available_ram_gb > min_required_ram:
                break  # Ресурсы есть, выходим из цикла ожидания

            logger.warning(f"[{filename}] System RAM critically low ({available_ram_gb:.1f}GB). Waiting...")

            # пишем напрямую в консоль (переписывая строку), чтобы видеть зависание в реальном времени
            print(f"\r{filename} waiting for RAM... (Free: {available_ram_gb:.1f} GB)", end="", flush=True)
            time.sleep(5)

        # Затирание строки пустыми пробелами
        print("\r" + " " * 80 + "\r", end="", flush=True)
    except Exception as mem_err:
        logger.error(f"Memory check failed: {mem_err}")

    # 2. Запуск обработки
    logger.info(f"=== [File {file_index} of {total_files}] === [{filename}] ===")
    try:
        # Если файл потребует больше WORKER_MAX_RAM_GB, эта строка выбросит MemoryError
        with ProcessProfiler() as profiler:
            FastAcquisition1To3GHzObservationProcessor.execute(bin_file, output_fits_file, overwrite)
        success = True
        exec_time = profiler.elapsed_seconds
        peak_ram = profiler.peak_memory_mb
        logger.info(f"[{filename}] Stats -> Time: {profiler.formatted_time} | Peak RAM: {profiler.peak_memory_mb:.1f} MB")
    except MemoryError:
        error_msg = f"Memory Limit Exceeded (>{max_worker_ram} GB)"
        logger.error(f"[{filename}] Fatal Error: {error_msg}")
    except Exception as e:
        error_msg = str(e)[:500]
        logger.error(f"[{filename}] Fatal Pipeline Error: {error_msg}", exc_info=True)
    finally:
        if list_handler:
            captured_logs = list_handler.records

    return WorkerResult(filename, success, error_msg, captured_logs, exec_time, peak_ram)