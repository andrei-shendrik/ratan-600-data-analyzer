import argparse
import sys
from pathlib import Path

from src.apps.bin2fits_fast_acquisition_1_3ghz.bin2fits_fast_acqusition_1_3ghz_app import Bin2FitsFastAcquisitionApp
from src.apps.bin2fits_fast_acquisition_1_3ghz.infrastructure.database import init_db
from src.apps.bin2fits_fast_acquisition_1_3ghz.scripts.check_db import check_db
from src.apps.bin2fits_fast_acquisition_1_3ghz.settings.bin2fits_fast_acquisition_1_3ghz_settings import \
    Bin2FitsFastAcquisition1To3GHzSettings
from src.ratan_600_data_analyzer.common.project_info import ProjectInfo
from src.ratan_600_data_analyzer.logging.logger_configurator import LoggerConfigurator, get_logger

logger = get_logger(__name__)

#@time_counter
def main():

    # settings
    try:
        project_root = ProjectInfo.find_project_root()
        current_dir = Path(__file__).resolve().parent
        env_file = project_root / ".env"
        toml_file = current_dir / "config" / "config.toml"

        app_settings = Bin2FitsFastAcquisition1To3GHzSettings.load(
            env_path=env_file,
            toml_path=toml_file
        )
    except Exception as e:
        logger.critical(f"Error load config:\n{e}")
        raise

    # logging
    configurator = LoggerConfigurator(app_settings.logging_settings)
    configurator.configure()

    # database initialization
    init_db(app_settings.database_settings.db_url)

    # test DB
    log_level = app_settings.logging_settings.log_level
    if log_level == "DEBUG":
        check_db(app_settings)

    # Console parsing
    # bin2fits_fast_1_3 --help
    parser = argparse.ArgumentParser(prog="bin2fits_fast_1_3",
                                     description="bin2fits_fast_1_3: Observation Conversion Utility from .bin to .fits fo Fast Acquisition 1-3GHz")
    parser.add_argument("--daemon", action="store_true", help="Watchdog, systemd service")
    parser.add_argument("--file", type=str, help="Convert chosen .bin file")

    parser.add_argument("--overwrite", action="store_true", help="Overwrite .fits file")
    parser.add_argument("--failed", action="store_true", help="Include .bin files for which conversion has failed")

    parser.add_argument("--bin-dir", type=str, help="directory for .bin files. Default: project settings")
    parser.add_argument("--fits-dir", type=str, help="directory for .fits files. Default: project settings")

    parser.add_argument("--start-date", type=str, help="Starting date, format: YYYYMMDD or YYYYMMDD_HHMMSS")
    parser.add_argument("--end-date", type=str, help="Ending date, format: YYYYMMDD or YYYYMMDD_HHMMSS")
    parser.add_argument("--day", type=str, help="Convert for specific day, format: YYYYMMDD")
    parser.add_argument("--month", type=str, help="Convert for specific month, format: YYYYMM")
    parser.add_argument("--year", type=str, help="Convert for specific year, format: YYYY")

    args = parser.parse_args()

    has_action = args.daemon or args.file
    has_filter = args.start_date or args.year or args.month or args.day

    # Если ничего не указано показать help и выйти
    if not (has_action or has_filter):
        parser.print_help()
        sys.exit(0)

    # start app
    app = Bin2FitsFastAcquisitionApp(app_settings)
    try:
        if args.daemon:
            app.run_daemon()
        else:
            app.run_cli_batch(args)
    except KeyboardInterrupt:
        logger.info("Ctrl+C: Canceled by user")

def print_settings_info(app_settings: Bin2FitsFastAcquisition1To3GHzSettings):
    logger.debug("debug message")
    logger.debug(f"Logger level: {app_settings.logging_settings.log_level}")
    logger.debug(f"Base dir: {app_settings.logging_settings.base_dir}")
    logger.debug(f"Fits archive: {app_settings.fits_archive}")

    # logger.info(f"info message")
    # logger.warning("warning message")
    # logger.error("error message")

if __name__ == "__main__":
    main()