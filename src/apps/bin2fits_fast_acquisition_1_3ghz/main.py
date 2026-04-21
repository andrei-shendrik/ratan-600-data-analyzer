import logging
import sys

from apps.bin2fits_fast_acquisition_1_3ghz.bin2fits_fast_acquisition_1_3ghz_app import Bin2FitsFastAcquisitionApp
from apps.bin2fits_fast_acquisition_1_3ghz.cli.cli_parser import CliParser
from apps.bin2fits_fast_acquisition_1_3ghz.infrastructure.database import init_db
from apps.bin2fits_fast_acquisition_1_3ghz.settings.bin2fits_fast_acquisition_1_3ghz_settings import \
    Bin2FitsFastAcquisition1To3GHzSettings
from ratan_600_data_analyzer.common.project_info import ProjectInfo
from ratan_600_data_analyzer.logging.logger_configurator import LoggerConfigurator

logger = logging.getLogger(__name__)

#@time_counter
def main():

    # init settings
    try:
        project_info = ProjectInfo()
        project_root = project_info.project_root
        env_file = project_root / ".env"
        app_conf_toml = project_root / "config" / "bin2fits_fast_1_3_app.toml"

        if not env_file.is_file():
            logger.critical(f".env file not found at {env_file}")
            sys.exit(1)

        if not app_conf_toml.is_file():
            logger.critical(f"Application config not found at {app_conf_toml}")
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Error:\n{e}")
        sys.exit(1)

    app_settings = Bin2FitsFastAcquisition1To3GHzSettings.load(
        env_path=env_file,
        toml_path=app_conf_toml
    )

    # logging
    configurator = LoggerConfigurator(app_settings.logging_settings)
    configurator.configure()

    # database initialization
    init_db(app_settings.database_settings.db_url)

    # test DB
    log_level = app_settings.logging_settings.log_level
    if log_level == "DEBUG":
        # check_db(app_settings)
        from apps.bin2fits_fast_acquisition_1_3ghz.scripts.check_db import check_database, show_processing_files, \
            show_failed_files

        check_database(app_settings)  # Покажет сколько всего записей
        show_processing_files(app_settings)  # Покажет, есть ли сейчас активные/зависшие процессы
        show_failed_files(app_settings)  # Покажет, на чем падали последние конвертации

    # console parser
    cli_parser = CliParser()
    args = cli_parser.parse()

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
    logger.debug(f"Log dir: {app_settings.logging_settings.base_dir}")
    logger.debug(f"Fits archive: {app_settings.fits_archive}")

if __name__ == "__main__":
    main()