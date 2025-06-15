import os

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