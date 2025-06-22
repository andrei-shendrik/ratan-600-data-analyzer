import copy


class FitsHeaderReader:
    def __init__(self, header):
        self._header = copy.deepcopy(header)

    def get_value(self, keyword: str, required=True):
        """
            Получение параметра из заголовка fits файла

            Case-sensitive
        """
        if required and keyword not in self._header:
            raise KeyError(f"Keyname '{keyword}' not found in the header.")
        value = self._header.get(keyword)
        return value

    def get_comment(self, keyword: str):
        card = self._header.cards[keyword]
        return card.comment

    def keyword_exists(self, keyword: str) -> bool:
        if keyword in self._header:
            return True
        else:
            return False