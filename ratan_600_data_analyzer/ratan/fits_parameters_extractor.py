import copy

import numpy as np


class FitsParametersExtractor:
    def __init__(self, header):
        self._header = copy.deepcopy(header)

    def get_fits_header_value(self, param_name: str, required=True):
        """
            Получение параметра из заголовка fits файла

            Case-sensitive
        """
        if required and param_name not in self._header:
            raise KeyError(f"Parameter '{param_name}' not found in the header.")
        value = self._header.get(param_name)
        return value
