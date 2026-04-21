import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.bin2fits_fast_acquisition_1_3ghz.cli.cli_batch_handler import CliBatchHandler
from apps.bin2fits_fast_acquisition_1_3ghz.daemon.watcher import Watcher
from apps.bin2fits_fast_acquisition_1_3ghz.services.processing_controller import \
    FastAcquisition1To3GHzProcessingController

logger = logging.getLogger(__name__)


class Bin2FitsFastAcquisitionApp:
    def __init__(self, settings):
        self._settings = settings

        self._engine = create_engine(settings.database_settings.db_url)
        self._session_local = sessionmaker(bind=self._engine)

        self._processing_controller = FastAcquisition1To3GHzProcessingController(
            session_factory=self._session_local,
            settings=self._settings
        )

        # восстановление зависших статусов DB 'processing'
        self._processing_controller.recover_stuck_files(timeout_minutes=10)

    def run_daemon(self):
        """
            Daemon mode (Watchdog)
        """
        daemon = Watcher(
            processing_controller=self._processing_controller,
            settings=self._settings
        )
        daemon.start()

    def run_cli_batch(self, args):
        """
            Manual mode
        """
        handler = CliBatchHandler(self._processing_controller, self._settings)
        handler.execute(args)