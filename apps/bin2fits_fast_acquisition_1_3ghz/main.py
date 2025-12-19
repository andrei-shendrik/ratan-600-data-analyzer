import time

from apps.bin2fits_fast_acquisition_1_3ghz.settings.config import app_settings, error_tracker
from apps.bin2fits_fast_acquisition_1_3ghz.logging.logger_configurator import get_logger

logger = get_logger(__name__)

def time_counter(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"'{func.__name__}' execution time {execution_time:.4f} sec")
        return result
    return wrapper

@time_counter
def main():
    print_settings_info()

def print_settings_info():
    logger.debug("debug message")
    logger.debug(f"Logger level: {app_settings.logging.log_level}")
    logger.debug(f"Log path: {app_settings.logging.log_path}")
    logger.debug(f"Fits archive: {app_settings.fits_archive}")

    error_tracker.add("test")

    # logger.info(f"info message")
    # logger.warning("warning message")
    # logger.error("error message")

if __name__ == "__main__":
    main()