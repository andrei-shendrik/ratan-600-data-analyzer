import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List

from filelock import FileLock, Timeout
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apps.bin2fits_fast_acquisition_1_3ghz.infrastructure.database import FastAcquisition1To3GHzRaw, ProcessingStatus
from apps.bin2fits_fast_acquisition_1_3ghz.services.observation_processor import FastAcquisition1To3GHzObservationProcessor

logger = logging.getLogger(__name__)

@dataclass
class BatchReport:
    total: int
    success: int
    failed: int
    processing: int
    unprocessed: int
    failed_filenames: List[str]

class FastAcquisition1To3GHzProcessingController:
    def __init__(self, session_factory, settings):
        self._session_factory = session_factory
        self._settings = settings

    def recover_stuck_files(self, timeout_minutes: int = 10):
        """
            Ищет в БД файлы со статусом PROCESSING, которые висят дольше timeout_minutes.
            Переводит статус обратно в UNPROCESSED.
        """
        session: Session | None = None
        try:
            session = self._session_factory()
            if session is not None:
                cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)

                # поиск зависших записей
                stmt = select(FastAcquisition1To3GHzRaw).where(
                    FastAcquisition1To3GHzRaw.status == ProcessingStatus.PROCESSING,
                    FastAcquisition1To3GHzRaw.updated_at < cutoff_time
                )
                stuck_records = session.scalars(stmt).all()

                recovered_count = 0
                for record in stuck_records:
                    filename = record.bin_filename
                    fits_path = Path(record.fits_path_filename) if record.fits_path_filename else None

                    # удаление "недописанного" или "старого" .fits файла
                    if fits_path and fits_path.exists():
                        try:
                            os.remove(fits_path)
                            logger.warning(
                                f"File {fits_path.name} was deleted due to stuck status 'processing'. Status set to 'unprocessed'")
                        except Exception as file_err:
                            logger.error(f"Unable to delete file '{fits_path.name}': {file_err}")

                    # откат статуса в БД
                    record.status = ProcessingStatus.UNPROCESSED
                    record.fits_filename = None
                    record.fits_path_filename = None
                    record.comment = "Stuck status 'processing' detected (Timeout). Fits file removed. Status reverted to UNPROCESSED."
                    recovered_count += 1

                if recovered_count > 0:
                    session.commit()
                    logger.warning(f"Recovered {recovered_count} stuck DB entries")

        except Exception as e:
            if session is not None: session.rollback()
            logger.error(f"Error stuck recovery: {e}")
        finally:
            if session is not None: session.close()

    def get_output_fits_pathfilename(self, bin_file: Path, fits_base_dir: Path) -> Path:
        bin_archive = self._settings.bin_archive.resolve()
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
        should_use_db = bin_file.is_relative_to(self._settings.bin_archive.resolve()) and \
                        output_fits_file.is_relative_to(self._settings.fits_archive.resolve())

        if output_fits_file.exists() and not overwrite:
            logger.debug(f"[{filename}] processing not needed: FITS file already exists (use --overwrite)")
            return False

        if should_use_db:
            with self._session_factory() as session:
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
        should_use_db = bin_file.is_relative_to(self._settings.bin_archive.resolve()) and \
                        output_fits_file.is_relative_to(self._settings.fits_archive.resolve())

        if not should_use_db:
            lock_path = str(output_fits_file) + ".lock"
            lock = FileLock(lock_path, timeout=0)  # timeout=0 означает "не ждать, если занято"
            try:
                lock.acquire()  # Пытаемся захватить файл
                # ВАЖНО: Мы должны вернуть объект lock, чтобы снять его в конце!
                # В данной архитектуре лучше сделать так, чтобы Lock жил, пока жив процесс воркера.
                # Так как ОС сама удаляет локи FileLock при смерти процесса - это будет работать идеально.
                return output_fits_file
            except Timeout:
                logger.warning(f"[{bin_file.name}] Conflict: File is locked by OS.")
                return None

        session: Session | None = None
        try:
            session = self._session_factory()
            if session is not None:
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
        should_use_db = bin_file.is_relative_to(self._settings.bin_archive.resolve())
        if not should_use_db:
            return

        session: Session | None = None
        try:
            session = self._session_factory()
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

    def generate_batch_report(self, processed_files: List[Path]) -> BatchReport:
        """
        Generates a summary report for a specific batch of files.
        Automatically cleans up any STUCK (PROCESSING) statuses left behind by crashed workers.
        """
        if not processed_files:
            return BatchReport(0, 0, 0, 0, 0, [])

        filenames = [f.name for f in processed_files]
        report = BatchReport(total=len(filenames), success=0, failed=0, processing=0, unprocessed=0,
                             failed_filenames=[])

        session: Session | None = None
        try:
            session = self._session_factory()
            if session is not None:
                # 1. Запрашиваем статусы из БД только для наших файлов
                stmt = select(FastAcquisition1To3GHzRaw).where(
                    FastAcquisition1To3GHzRaw.bin_filename.in_(filenames)
                )
                records = session.scalars(stmt).all()

                # Считаем статусы и собираем имена упавших файлов
                stuck_records = []
                for record in records:
                    if record.status == ProcessingStatus.SUCCESS:
                        report.success += 1
                    elif record.status == ProcessingStatus.FAILED:
                        report.failed += 1
                        report.failed_filenames.append(record.bin_filename)
                    elif record.status == ProcessingStatus.UNPROCESSED:
                        report.unprocessed += 1
                    elif record.status == ProcessingStatus.PROCESSING:
                        report.processing += 1
                        stuck_records.append(record)

                # 2. АВТО-ОЧИСТКА ЗАВИСШИХ СТАТУСОВ (Cleanup)
                if stuck_records:
                    logger.warning(
                        f"Batch Cleanup: Found {len(stuck_records)} files stuck in PROCESSING state. Reverting them...")
                    for record in stuck_records:
                        fits_path = Path(record.fits_path_filename) if record.fits_path_filename else None

                        if fits_path and fits_path.exists():
                            # Перезапись упала, возвращаем старый SUCCESS
                            record.status = ProcessingStatus.SUCCESS
                            record.comment = "Cleanup: Worker crashed during overwrite. Reverted to original SUCCESS."
                            report.success += 1
                            report.processing -= 1
                        else:
                            # Обычный краш
                            record.status = ProcessingStatus.FAILED
                            record.fits_filename = None
                            record.fits_path_filename = None
                            record.comment = "Cleanup: Worker crashed (No FITS file found)."
                            report.failed += 1
                            report.processing -= 1
                            report.failed_filenames.append(record.bin_filename)

                    session.commit()
                    logger.warning("Batch Cleanup: Successfully reverted stuck statuses.")

        except Exception as e:
            if session is not None: session.rollback()
            logger.error(f"Failed to generate batch report: {e}")
        finally:
            if session is not None: session.close()

        return report

    def revert_claim(self, bin_file: Path):
        """Откатывает бронь файла (возвращает в UNPROCESSED)"""
        filename = bin_file.name
        session: Session | None = None
        try:
            session = self._session_factory()
            if session is not None:
                stmt = select(FastAcquisition1To3GHzRaw).filter_by(bin_filename=filename)
                record: FastAcquisition1To3GHzRaw | None = session.scalar(stmt)
                if record is not None:
                    if record.status == ProcessingStatus.PROCESSING:
                        record.status = ProcessingStatus.UNPROCESSED
                        record.fits_filename = None
                        record.fits_path_filename = None
                        record.comment = "Aborted before processing finished"
                        session.commit()
                        logger.warning(f"[{filename}] Status reverted to UNPROCESSED.")
        except Exception as e:
            if session is not None: session.rollback()
            logger.error(f"[{filename}] Failed to revert claim: {e}")
        finally:
            if session is not None: session.close()