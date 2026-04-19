import argparse
import logging
import sys

logger = logging.getLogger(__name__)

class CliParser:
    """
        Console parsing
        bin2fits_fast_1_3 --help
    """
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog="bin2fits_fast_1_3",
            description="Observation Conversion Utility from .bin to .fits fo Fast Acquisition 1-3GHz"
        )
        self._setup_arguments()

    def _setup_arguments(self):
        p = self.parser
        p.add_argument("--daemon", action="store_true", help="Watchdog, systemd service")
        p.add_argument("--file", type=str, help="Convert chosen .bin file")

        p.add_argument("--overwrite", action="store_true", help="Overwrite .fits file")
        p.add_argument("--failed", action="store_true", help="Include .bin files for which conversion has failed")

        p.add_argument("--bin-dir", type=str, help="directory for .bin files. Default: project settings")
        p.add_argument("--fits-dir", type=str, help="directory for .fits files. Default: project settings")

        p.add_argument("--start-date", type=str, help="Starting date, format: YYYYMMDD or YYYYMMDD_HHMMSS")
        p.add_argument("--end-date", type=str, help="Ending date, format: YYYYMMDD or YYYYMMDD_HHMMSS")
        p.add_argument("--day", type=str, help="Convert for specific day, format: YYYYMMDD")
        p.add_argument("--month", type=str, help="Convert for specific month, format: YYYYMM")
        p.add_argument("--year", type=str, help="Convert for specific year, format: YYYY")

        p.add_argument("--workers", type=int, default=1, help="Number of parallel processes. Default: 1 (sequential). Use >1 for multi-processing")

    def parse(self) -> argparse.Namespace:
        args = self.parser.parse_args()

        has_action = args.daemon or args.file
        has_filter = args.start_date or args.year or args.month or args.day

        if not (has_action or has_filter):
            self.parser.print_help()
            sys.exit(0)

        return args