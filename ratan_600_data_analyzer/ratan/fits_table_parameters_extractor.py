import copy

import numpy as np


class FitsTableParametersExtractor:
    def __init__(self, hdu_table):
        self._hdu_table = copy.deepcopy(hdu_table)

    def get_array(self, param_name: str, required=True):
        """
            Получение параметра из второго заголовка fits файла

            Case-sensitive
        """
        if required and param_name not in self._hdu_table.dtype.names:
            raise KeyError(f"Parameter '{param_name}' not found in the hdu table.")
        array = self._hdu_table[param_name].astype(np.float32)
        return array