from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.bin2fits_fast_acquisition_1_3ghz.infrastructure.database import FastAcquisition1To3GHzRaw, ProcessingStatus
from ratan_600_data_analyzer.logging.logger_configurator import get_logger
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_fits_writer import \
    FastAcquisition1To3GHzFitsWriter
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import \
    FastAcquisition1To3GHzObservation
from ratan_600_data_analyzer.ratan.ratan_builder_factory import RatanBuilderFactory

logger = get_logger(__name__)

class ObservationProcessor:
    def __init__(self, session_factory, settings):
        self.session_factory = session_factory
        self.settings = settings

    def is_needed_to_process(self, bin_file: Path, fits_base_dir: Path, overwrite: bool = False,
                     retry_failed: bool = False) -> bool:
        """

        """
        bin_file = bin_file.resolve()
        filename = bin_file.name

        bin_archive = self.settings.bin_archive.resolve()
        fits_archive = self.settings.fits_archive.resolve()
        is_in_bin_archive = bin_file.is_relative_to(bin_archive)

        if filename.endswith('.bin.gz'):
            fits_filename = filename.replace('.bin.gz', '.fits').lower()
        else:
            fits_filename = bin_file.with_suffix('.fits').name.lower()

        if is_in_bin_archive:
            year_month = bin_file.parent.relative_to(bin_archive)
            output_fits_dir = fits_base_dir / year_month
        else:
            output_fits_dir = fits_base_dir

        output_fits_file = output_fits_dir / fits_filename
        is_in_fits_archive = output_fits_file.is_relative_to(fits_archive)
        should_use_db = is_in_bin_archive and is_in_fits_archive

        if output_fits_file.exists() and not overwrite:
            logger.debug(f"[{filename}] skipped: FITS file already exists (use flag --overwrite)")
            return False

        if should_use_db:
            with self.session_factory() as session:
                stmt = select(FastAcquisition1To3GHzRaw).filter_by(bin_filename=filename)
                existing_record = session.scalar(stmt)
                if existing_record:
                    if existing_record.status == ProcessingStatus.SUCCESS and not overwrite and output_fits_file.exists():
                        logger.debug(f"[{filename}] skipped: DB status is SUCCESS (use flag --overwrite)")
                        return False
                    if existing_record.status == ProcessingStatus.FAILED and not retry_failed and not overwrite:
                        logger.debug(f"[{filename}] skipped: DB status is FAILED. Use flag --failed to retry")
                        return False
        return True

    def process_file(self, bin_file: Path, fits_base_dir: Path, overwrite: bool = False, retry_failed: bool = False):
        if not self.is_needed_to_process(bin_file, fits_base_dir, overwrite, retry_failed):
            return

        bin_file = bin_file.resolve()
        filename = bin_file.name

        bin_archive = self.settings.bin_archive.resolve()
        fits_archive = self.settings.fits_archive.resolve()
        is_in_bin_archive = bin_file.is_relative_to(bin_archive)

        if filename.endswith('.bin.gz'):
            fits_filename = filename.replace('.bin.gz', '.fits').lower()
        else:
            fits_filename = bin_file.with_suffix('.fits').name.lower()

        if is_in_bin_archive:
            year_month = bin_file.parent.relative_to(bin_archive)
            output_fits_dir = fits_base_dir / year_month
        else:
            output_fits_dir = fits_base_dir

        output_fits_dir.mkdir(parents=True, exist_ok=True)
        output_fits_file = output_fits_dir / fits_filename

        is_in_fits_archive = output_fits_file.is_relative_to(fits_archive)
        should_use_db = is_in_bin_archive and is_in_fits_archive

        if not should_use_db:
            logger.info(f"[{filename}] Processing outside archives: disable write to DB")

        # БД
        session: Session | None = None
        existing_record: FastAcquisition1To3GHzRaw | None = None

        try:
            if should_use_db:
                session = self.session_factory()
                if session is not None:
                    stmt = select(FastAcquisition1To3GHzRaw).filter_by(bin_filename=filename)
                    existing_record = session.scalar(stmt)

            # processing
            logger.info(f"[{filename}]: started processing")
            builder = RatanBuilderFactory.create_builder(bin_file)
            observation = None

            if RatanBuilderFactory.is_fast_1_3ghz_builder(builder):
                observation = (builder
                               .read()
                               .remove_spikes(method="kurtosis")
                               .calibrate(method="lebedev")
                               .build())

            if observation is None:
                logger.error(f"Processing failed, no .fits file created")
                raise Exception()

            if isinstance(observation, FastAcquisition1To3GHzObservation):
                writer = FastAcquisition1To3GHzFitsWriter(observation)
                writer.write(output_fits_file, overwrite)
            else:
                logger.error(f"Failed to write observation")
                raise Exception()

            logger.info(f"[{filename}] successfully converted to: {output_fits_file}")

            if session is not None:
                self._save_to_db(
                    session=session,
                    record=existing_record,
                    bin_path=bin_file,
                    fits_path=output_fits_file,
                    status=ProcessingStatus.SUCCESS,
                    comment=""
                )

        except Exception as e:
            error_msg = str(e)[:500]
            logger.error(f"[{filename}] processing error: {e}", exc_info=True)
            if session is not None:
                try:
                    self._save_to_db(
                        session=session,
                        record=existing_record,
                        bin_path=bin_file,
                        fits_path=None,
                        status=ProcessingStatus.FAILED,
                        comment=error_msg
                    )
                except Exception as db_fallback_err:
                    logger.critical(f"Failed to save FAILED status to DB: {db_fallback_err}")
        finally:
            if session is not None:
                session.close()

    def _save_to_db(
            self,
            session: Session,
            record: FastAcquisition1To3GHzRaw | None,
            bin_path: Path,
            fits_path: Path | None,
            status: ProcessingStatus,
            comment: str
    ):
        """
        Сохраняет или обновляет запись в базе данных.
        Защищено блоком try-except для предотвращения зависания транзакции.
        """
        try:
            if not record:
                # Используем правильные имена полей из ORM модели
                record = FastAcquisition1To3GHzRaw(
                    bin_path_filename=str(bin_path),
                    bin_filename=bin_path.name
                )
                session.add(record)

            record.fits_path_filename = str(fits_path) if fits_path else None
            record.fits_filename = fits_path.name if fits_path else None
            record.status = status
            record.comment = comment[:2000] if comment else None
            session.commit()

        except Exception as db_err:
            # Обязательно откатываем сессию при ошибке коммита (например, уникальность ключа)
            session.rollback()
            logger.critical(f"Database error while saving record for {bin_path.name}: {db_err}")
            raise  # Перехватываем на уровне выше (или логгируем и идём дальше)