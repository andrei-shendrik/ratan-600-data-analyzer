import json
import re
from pathlib import Path
from typing import Dict, Any

from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.json_data import JSONData


class DescReader:

    def __init__(self):
        pass

    def read(self, desc_file: Path) -> JSONData:
        try:
            with open(desc_file, 'r', encoding='utf-8') as f:

                json_lines = [
                    self._fix_line(line)
                    for line in f
                    if not line.strip().startswith('#') and line.strip()
                ]
                json_data = json.loads(''.join(json_lines))
                return JSONData(json_data)

        except FileNotFoundError:
            raise RuntimeError(f"File not found: {self._desc_file}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON format: {str(e)}")

    def _fix_line(self, line: str) -> str:
        """
            Исправление неправильного формата json
            False -> false
        """
        line = re.sub(r'\bTrue\b', 'true', line, flags=re.IGNORECASE)
        line = re.sub(r'\bFalse\b', 'false', line, flags=re.IGNORECASE)
        return line