from typing import Dict, Any


class JSONData:

    def __init__(self, data: Dict[str, Any]):
        self._json_data = data

    def get_value(self, key_path: str, default: Any = None) -> Any:
        keys = key_path.split('.')
        current = self._json_data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    @property
    def json_data(self) -> Dict[str, Any]:
        return self._json_data