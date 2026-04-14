from pathlib import Path
from typing import Dict, Any

from pydantic import BaseModel, Field, field_validator


class LoggingSettings(BaseModel):
    base_dir: Path
    log_level: str = "INFO"
    console_output: bool = True
    log_format: str
    date_format: str
    rotation_size_mb: int
    handlers: Dict[str, str]

    @field_validator("handlers", mode="before")
    @classmethod
    def parse_handlers(cls, v: Any) -> Dict[str, str]:
        if isinstance(v, list):
            return {h.get("level", "INFO").upper(): h.get("filename") for h in v if "filename" in h}
        return v