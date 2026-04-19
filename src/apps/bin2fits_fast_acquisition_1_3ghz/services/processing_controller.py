import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apps.bin2fits_fast_acquisition_1_3ghz.infrastructure.database import FastAcquisition1To3GHzRaw, ProcessingStatus
from apps.bin2fits_fast_acquisition_1_3ghz.services.observation_processor import FastAcquisition1To3GHzObservationProcessor

logger = logging.getLogger(__name__)

class FastAcquisition1To3GHzProcessingController:
    def __init__(self, session_factory, settings):
        self.session_factory = session_factory
        self.settings = settings

    def get_output_fits_pathfilename(self, bin_file: Path, fits_base_dir: Path) -> Path:
        bin_archive = self.settings.bin_archive.resolve()
        filename = bin_file.name

        if filename.endswith('.bin.gz'):
            fits_filename = filename.replace('.bin.gz', '.fits').lower()
        else:
            fits_filename = bin_file.with_suffix('.fits').name.lower()

        if bin_file.is_relative_to(bin_archive):
            year_month = bin_file.parent.relative_to(bin_archive)
            output_fits_dir = fits_base_dir / year_month
        else:
            output_fits_dir = fits_base_dir

        output_fits_dir.mkdir(parents=True, exist_ok=True)
        return output_fits_dir / fits_filename

    def is_needed_to_process(self, bin_file: Path, fits_base_dir: Path, overwrite: bool = False, retry_failed: bool = False) -> bool:
        """
            Определяет, нужно ли обрабатывать файл
        """
        filename = bin_file.name
        output_fits_file = self.get_output_fits_pathfilename(bin_file, fits_base_dir)
        should_use_db = bin_file.is_relative_to(self.settings.bin_archive.resolve()) and \
                        output_fits_file.is_relative_to(self.settings.fits_archive.resolve())

        if output_fits_file.exists() and not overwrite:
            logger.debug(f"[{filename}] processing not needed: FITS file already exists (use --overwrite)")
            return False

        if should_use_db:
            with self.session_factory() as session:
                stmt = select(FastAcquisition1To3GHzRaw).filter_by(bin_filename=filename)
                existing_record = session.scalar(stmt)
                if existing_record:
                    if existing_record.status == ProcessingStatus.PROCESSING:

                        last_update = existing_record.updated_at
                        # Если нет таймзоны (наивное время), добавляем UTC, чтобы можно было сравнивать
                        if last_update.tzinfo is None:
                            last_update = last_update.replace(tzinfo=timezone.utc)

                        now = datetime.now(timezone.utc)
                        time_diff = now - last_update

                        # Если файл "обрабатывается" дольше 10 минут - считаем процесс мертвым
                        if time_diff > timedelta(minutes=10):
                            logger.warning(
                                f"[{filename}] Detected STUCK status (Processing for {time_diff}). Allowing retry.")
                            return True
                        else:
                            logger.debug(f"[{filename}] processing not needed: Currently processing by another worker")
                            return False
                    if existing_record.status == ProcessingStatus.SUCCESS and not overwrite and output_fits_file.exists():
                        logger.debug(f"[{filename}] processing not needed: DB status is SUCCESS")
                        return False
                    if existing_record.status == ProcessingStatus.FAILED and not retry_failed and not overwrite:
                        logger.debug(f"[{filename}] processing not needed: DB status is FAILED. Use flag --failed")
                        return False
        return True

    def claim_file_for_processing(self, bin_file: Path, fits_base_dir: Path) -> Path | None:
        """
            Бронь файла в БД (статус PROCESSING) для дальнейшей обработки. Возврат None, если занят другим процессом.
        """
        output_fits_file = self.get_output_fits_pathfilename(bin_file, fits_base_dir)
        filename = bin_file.name
        should_use_db = bin_file.is_relative_to(self.settings.bin_archive.resolve()) and \
                        output_fits_file.is_relative_to(self.settings.fits_archive.resolve())

        if not should_use_db:
            return output_fits_file

        session: Session | None = None
        try:
            session = self.session_factory()
            if session is not None:
                # ====================================================================
                # --- ИЗМЕНЕНО: СУПЕР-ЗАЩИТА ОТ WINERROR 32 (.bin vs .bin.gz) ---
                # Ищем, не занял ли кто-то (другой исходник) наш целевой FITS-файл
                # ====================================================================
                stmt_fits = select(FastAcquisition1To3GHzRaw).filter_by(fits_filename=output_fits_file.name)
                existing_fits_claim = session.scalar(stmt_fits)

                if existing_fits_claim and existing_fits_claim.bin_filename != filename:
                    logger.warning(
                        f"[{filename}] Conflict averted: FITS file '{output_fits_file.name}' is already claimed by '{existing_fits_claim.bin_filename}'.")
                    return None
                # ====================================================================

                stmt = select(FastAcquisition1To3GHzRaw).filter_by(bin_filename=filename)
                record = session.scalar(stmt)

                if record:
                    record.status = ProcessingStatus.PROCESSING
                    record.fits_filename = output_fits_file.name
                    record.fits_path_filename = str(output_fits_file)
                    record.comment = ""
                else:
                    record = FastAcquisition1To3GHzRaw(
                        bin_path_filename=str(bin_file),
                        bin_filename=filename,
                        fits_filename=output_fits_file.name,
                        fits_path_filename=str(output_fits_file),
                        status=ProcessingStatus.PROCESSING,
                        comment=""
                    )
                    session.add(record)
                session.commit()
                return output_fits_file

        except IntegrityError:
            if session is not None: session.rollback()
            logger.warning(f"[{filename}] Conflict averted: The target FITS file is claimed by another process.")
            return None
        except Exception as e:
            if session is not None: session.rollback()
            logger.error(f"[{filename}] DB Claim error: {e}")
            return None
        finally:
            if session is not None: session.close()

    def finalize_status_in_db(self, bin_file: Path, fits_path: Path | None, status: ProcessingStatus, comment: str):
        """
            Обновление статуса обработки (SUCCESS/FAILED)
        """
        should_use_db = bin_file.is_relative_to(self.settings.bin_archive.resolve())
        if not should_use_db:
            return

        session: Session | None = None
        try:
            session = self.session_factory()
            if session is not None:
                stmt = select(FastAcquisition1To3GHzRaw).filter_by(bin_filename=bin_file.name)
                record = session.scalar(stmt)
                if record:
                    record.fits_path_filename = str(fits_path) if fits_path else None
                    record.fits_filename = fits_path.name if fits_path else None
                    record.status = status
                    record.comment = comment[:2000] if comment else None
                    session.commit()
        except Exception as db_err:
            if session is not None: session.rollback()
            logger.critical(f"DB Error on finalize {bin_file.name}: {db_err}")
        finally:
            if session is not None: session.close()

    def process_file(self, bin_file: Path, fits_base_dir: Path, overwrite: bool = False, retry_failed: bool = False):
        if not self.is_needed_to_process(bin_file, fits_base_dir, overwrite, retry_failed):
            return

        output_fits_file = self.claim_file_for_processing(bin_file, fits_base_dir)
        if not output_fits_file:
            return

        try:
            FastAcquisition1To3GHzObservationProcessor.execute(bin_file, output_fits_file, overwrite)
            self.finalize_status_in_db(bin_file, output_fits_file, ProcessingStatus.SUCCESS, "")
        except Exception as e:
            error_msg = str(e)[:500]
            logger.error(f"[{bin_file.name}] Processing error: {error_msg}", exc_info=True)
            self.finalize_status_in_db(bin_file, None, ProcessingStatus.FAILED, error_msg)