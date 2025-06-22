import copy

import numpy as np


class FitsBinTableReader:
    def __init__(self, bin_table):
        self._bin_table = copy.deepcopy(bin_table)

    def get_column(self, keyword: str, required=True):
        """
            Чтение колонки бинарной таблицы fits файла
            Case-sensitive
        """
        if required and keyword not in self._bin_table.dtype.names:
            raise KeyError(f"Keyword '{keyword}' not found in the bin table.")
        array = self._bin_table[keyword].astype(np.float32)
        return array

    # todo
    def column_exists(self, keyword: str) -> bool:
        pass