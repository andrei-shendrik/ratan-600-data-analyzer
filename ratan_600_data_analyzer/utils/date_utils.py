import datetime


class DateUtils:

    @staticmethod
    def parse_date(date_string: str, date_format: str) -> datetime:
        """

        """
        try:
            dt = datetime.datetime.strptime(date_string, date_format).astimezone(datetime.timezone.utc)
            return dt
        except ValueError as e:
            raise ValueError(
                f"Error when parsing date '{date_string}' with format '{date_format}': {e}"
            )
