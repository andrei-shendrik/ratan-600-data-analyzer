from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.bin2fits_fast_acquisition_1_3ghz.cli.handlers import CliBatchHandler
from apps.bin2fits_fast_acquisition_1_3ghz.daemon.watcher import Watcher
from apps.bin2fits_fast_acquisition_1_3ghz.services.observation_processor import ObservationProcessor
from src.ratan_600_data_analyzer.logging.logger_configurator import get_logger

logger = get_logger(__name__)


class Bin2FitsFastAcquisitionApp:
    def __init__(self, settings):
        self._settings = settings

        self._engine = create_engine(settings.database_settings.db_url)
        self._session_local = sessionmaker(bind=self._engine)

        self._obs_processor = ObservationProcessor(
            session_factory=self._session_local,
            settings=self._settings
        )

    def run_daemon(self):
        """
            Daemon mode (Watchdog)
        """
        daemon = Watcher(self._obs_processor, self._settings.bin_archive)
        daemon.start()

    def run_cli_batch(self, args):
        """
            Manual mode
        """
        handler = CliBatchHandler(self._obs_processor, self._settings)
        handler.execute(args)