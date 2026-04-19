import tomllib
from pathlib import Path
from typing import List

from dotenv import dotenv_values
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from ratan_600_data_analyzer.database.database_settings import DatabaseSettings
from ratan_600_data_analyzer.logging.logging_settings import LoggingSettings


class Bin2FitsFastAcquisition1To3GHzSettings(BaseSettings):
    database_settings: DatabaseSettings
    bin_archive: Path = Field(alias="FAST_ACQ_1_3GHZ_BIN_ARCHIVE")
    fits_archive: Path = Field(alias="FAST_ACQ_1_3GHZ_FITS_ARCHIVE")
    logging_settings: LoggingSettings

    file_filters: FileFilterSettings

    model_config = SettingsConfigDict(extra="ignore")

    @classmethod
    def load(cls, env_path: Path, toml_path: Path) -> 'Bin2FitsFastAcquisition1To3GHzSettings':
        with open(toml_path, "rb") as f:
            toml_data = tomllib.load(f)

        env_data = dotenv_values(env_path)

        log_dict = toml_data.get("logging", {})

        # подмена дефолтных значений
        log_dict["base_dir"] = env_data.get("BIN2FITS_FAST_ACQ_1_3GHZ_LOG_DIR")
        log_dict["log_level"] = env_data.get("BIN2FITS_FAST_ACQ_1_3GHZ_LOG_LEVEL", "INFO")
        log_dict["console_output"] = (env_data.get("BIN2FITS_FAST_ACQ_1_3GHZ_CONSOLE_OUTPUT") or "True").lower() in ("true",
                                                                                                                 "1",
                                                                                                                 "yes")
        filters_dict = toml_data.get("file_filters", {})

        return cls(
            database_settings=DatabaseSettings(**env_data),
            logging_settings=LoggingSettings(**log_dict),
            file_filters=FileFilterSettings(**filters_dict),
            **env_data
        )

class FileFilterSettings(BaseModel):
    allowed_patterns: List[str] = Field(default_factory=list)
    forbidden_patterns: List[str] = Field(default_factory=list)