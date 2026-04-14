from pathlib import Path


class FileUtils:

    @staticmethod
    def check_file_exists(file_path: Path):
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

    @staticmethod
    def check_is_file(file_path: Path):
        if not file_path.is_file():
            raise TypeError(f"This is a directory, not a file: {file_path}")

    @staticmethod
    def validate_file(file_path: Path):
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.is_file():
            raise TypeError(f"This is a directory, not a file: {file_path}")
