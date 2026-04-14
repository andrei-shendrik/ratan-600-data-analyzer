import os
import time

def time_counter(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"'{func.__name__}' execution time {execution_time:.4f} sec")
        return result

    return wrapper

class CommonUtils:

    @staticmethod
    def path_to_unix(path: str) -> str:
        """

        """
        # r"D:\data\astro\ratan-600\fast_acquisition_1_3ghz\1-3ghz\2024\08\2024-08-01_121957_sun+00.bin".replace("\\", "/")
        if os.name == "nt":  # Проверка, является ли операционная система Windows
            return path.replace('\\', '/')
        else:
            return path