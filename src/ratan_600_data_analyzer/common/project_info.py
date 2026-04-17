from importlib import metadata
from pathlib import Path


class ProjectInfo:

    _PACKAGE_NAME = "ratan-600-data-analyzer"

    def __init__(self):
        self._project_name = self._get_project_name()
        self._project_version = self._get_project_version()
        self._project_root = self._find_project_root()

    @classmethod
    def _get_project_name(cls) -> str:
        try:
            metadata.metadata(cls._PACKAGE_NAME)
            return cls._PACKAGE_NAME
        except metadata.PackageNotFoundError:
            raise RuntimeError(
                f"Critical error: '{cls._PACKAGE_NAME}' not installed in .venv"
            )

    @classmethod
    def _get_project_version(cls) -> str:
        try:
            return metadata.version(cls._PACKAGE_NAME)
        except metadata.PackageNotFoundError:
            raise RuntimeError(
                f"Critical error: unable to find version of '{cls._PACKAGE_NAME}'"
            )

    @staticmethod
    def get_code_location() -> Path:
        return Path(__file__).resolve().parent

    @staticmethod
    def _find_project_root(start_path: Path = None, markers: list = None) -> Path:
        if start_path is None:
            start_path = ProjectInfo.get_code_location()

        if markers is None:
            markers = [
                "pyproject.toml",
                "setup.py",
                ".git",
                "requirements.txt",
                "src",
                "README.md"
            ]

        current = start_path.resolve()

        while current != current.parent:
            if any((current / marker).exists() for marker in markers):
                return Path(current)
            current = current.parent
        raise FileNotFoundError(f"Project root not found from {start_path}")

    @property
    def project_name(self) -> str:
        return self._project_name

    @property
    def project_version(self) -> str:
        return self._project_version

    @property
    def project_root(self) -> Path:
        return self._project_root