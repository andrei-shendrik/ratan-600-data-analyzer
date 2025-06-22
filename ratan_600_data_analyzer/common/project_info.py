import tomllib
from pathlib import Path


class ProjectInfo:
    def __init__(self, toml_filename: str = "pyproject.toml"):

        project_root = ProjectInfo.find_project_root()
        self.toml_path = Path(project_root / toml_filename)
        if not self.toml_path.exists() and not self.toml_path.is_file():
            raise FileNotFoundError(f"Project file not found: {self.toml_path}")

        self._dict = ProjectInfo._load_toml(self.toml_path)
        self._project_name = self._get_project_name()
        self._project_version = self._get_project_version()

    def _get_project_name(self) -> str:
        project_section = self._dict.get("project", {})
        if name := project_section.get("name"):
            return name
        raise ValueError(f"Project name not found in [project] section of {self.toml_path}")

    def _get_project_version(self) -> str:
        project_section = self._dict.get("project", {})
        if version := project_section.get("version"):
            return version
        raise ValueError(f"Project version not found in [project] section of {self.toml_path}")

    @staticmethod
    def find_project_root(start_path: Path = None, markers: list = None) -> Path:
        if start_path is None:
            start_path = Path.cwd()

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
                return current
            current = current.parent
        raise FileNotFoundError(f"Project root not found from {start_path}")

    @staticmethod
    def _load_toml(toml_path: Path) -> dict:
        with open(toml_path, "rb") as f:
            return tomllib.load(f)

    @property
    def project_name(self) -> str:
        return self._project_name

    @property
    def project_version(self) -> str:
        return self._project_version