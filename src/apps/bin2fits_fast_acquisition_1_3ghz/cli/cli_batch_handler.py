import concurrent.futures
import logging
import re
import signal
import threading
from datetime import datetime
from pathlib import Path

from apps.bin2fits_fast_acquisition_1_3ghz.infrastructure.database import ProcessingStatus
from apps.bin2fits_fast_acquisition_1_3ghz.services.observation_file_filter import ObservationFileFilter
from apps.bin2fits_fast_acquisition_1_3ghz.services.observation_processor import \
    FastAcquisition1To3GHzObservationProcessor
from apps.bin2fits_fast_acquisition_1_3ghz.services.parallel_worker import WorkerResult, parallel_worker, init_worker

logger = logging.getLogger(__name__)


class CliBatchHandler:
    def __init__(self, processing_controller, settings):
        self._processing_controller = processing_controller
        self._settings = settings
        self._file_filter = ObservationFileFilter(self._settings.file_filters)

        self._shutdown_requested = False
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def execute(self, args):
        bin_files_dir = Path(args.bin_dir).resolve() if args.bin_dir else self._settings.bin_archive.resolve()
        fits_files_dir = Path(args.fits_dir).resolve() if args.fits_dir else self._settings.fits_archive.resolve()

        if not bin_files_dir.exists():
            logger.error(f"Bin dir doesnt exist: {bin_files_dir}")
            return

        logger.debug(f"Search for .bin files in directory: {bin_files_dir}")
        all_found_files = list(self._find_files(bin_files_dir, args))

        # Предварительная фильтрация
        files_to_process = []
        for file_path in all_found_files:
            # отклонение по имени файла
            if not self._file_filter.is_valid(file_path):
                continue

            if self._processing_controller.is_needed_to_process(file_path, fits_files_dir, args.overwrite, args.failed):
                files_to_process.append(file_path)

        num_files_to_process = len(files_to_process)
        if num_files_to_process == 0:
            logger.info("No files require processing.")
            return

        workers_count = args.workers if args.workers is not None else 1
        active_workers = min(workers_count, num_files_to_process)
        is_multi_processing = active_workers > 1

        mode = f"Parallel ({active_workers} workers)" if is_multi_processing else "single-processing (1 worker)"
        logger.info(f"Starting processing of {num_files_to_process} files in {mode} mode...")

        if not is_multi_processing:
            self._run_sequential(files_to_process, fits_files_dir, args.overwrite, num_files_to_process)
        else:
            self._run_parallel(files_to_process, fits_files_dir, args.overwrite, num_files_to_process, active_workers)

        logger.info("Processing task finished")

        # report
        logger.info("=== Summary report ===")

        report = self._processing_controller.generate_batch_report(files_to_process)

        logger.info(f"Total files processed : {report.total}")
        logger.info(f"SUCCESS               : {report.success}")

        if report.failed > 0:
            logger.info(f"FAILED                : {report.failed}")
        else:
            logger.info(f"FAILED                : 0")

        if report.unprocessed > 0:
            logger.warning(f"UNPROCESSED (Skipped) : {report.unprocessed} (Check logs for database or IO locks)")

        if report.processing > 0:
            logger.critical(
                f"STUCK (Processing)    : {report.processing} (CRITICAL: Database transaction failed during cleanup!)")

        if report.failed > 0 and logger.isEnabledFor(logging.DEBUG):
            logger.info("--- FAILED FILES LIST ---")
            for fname in report.failed_filenames:
                logger.info(f"[{fname}] status: FAILED")
            logger.info("-------------------------")

        logger.info("=== End report ===")

    def _run_sequential(self, files_to_process, fits_files_dir, overwrite, total_files):
        processed_count = 0

        for file_path in files_to_process:
            processed_count += 1
            filename = file_path.name
            logger.info(f"=== ["
                        f"File {processed_count} of {total_files}] === [{filename}] ===")

            out_fits = self._processing_controller.claim_file_for_processing(file_path, fits_files_dir)
            if not out_fits:
                continue

            success = False
            error_msg = ""
            try:
                FastAcquisition1To3GHzObservationProcessor.execute(file_path, out_fits, overwrite)
                success = True
            except Exception as exc:
                error_msg = str(exc)[:500]
                logger.error(f"[{filename}] Fatal Error: {error_msg}", exc_info=True)

            status = ProcessingStatus.SUCCESS if success else ProcessingStatus.FAILED
            self._processing_controller.finalize_status_in_db(
                file_path,
                self._processing_controller.get_output_fits_pathfilename(file_path,
                                                                         fits_files_dir) if success else None,
                status,
                error_msg
            )

    def _run_parallel(self, files_to_process, fits_files_dir, overwrite, total_files, active_workers):

        # семафор
        queue_semaphore = threading.Semaphore(active_workers * 2)
        future_to_file = {}
        claimed_files = set()  # Список файлов, которые мы забронировали в БД

        # Добавляем callback для освобождения семафора ---
        def task_done_callback(fut):
            queue_semaphore.release()

        with concurrent.futures.ProcessPoolExecutor(max_workers=active_workers,
                                                    initializer=init_worker) as executor:

            for file_index, file_path in enumerate(files_to_process, 1):

                # Проверка: если нажали Ctrl+C, ПРЕКРАЩАЕМ брать новые файлы
                if self._shutdown_requested:
                    logger.warning("Loop interruption: new files will not be processed")
                    break

                # Умный Acquire: ждем место в очереди, но проверяем Ctrl+C каждую секунду
                acquired = False
                while not acquired:
                    if self._shutdown_requested:
                        break  # Выходим из цикла ожидания
                    # Пытаемся занять семафор (таймаут 1 сек)
                    acquired = queue_semaphore.acquire(timeout=1.0)

                # Если вышли из-за Ctrl+C - завершаем добавление файлов
                if self._shutdown_requested:
                    break

                # 1. ЖДЕМ СВОБОДНОГО МЕСТА В ПУЛЕ (Блокировка главного потока)
                # queue_semaphore.acquire()

                # 2. Место появилось! Только теперь бронируем файл в БД
                out_fits = self._processing_controller.claim_file_for_processing(file_path, fits_files_dir)
                if not out_fits:
                    queue_semaphore.release()  # Если файл не удалось забронировать, возвращаем "билетик"
                    continue

                claimed_files.add(file_path)

                future = executor.submit(parallel_worker, file_path, out_fits, overwrite, self._settings, file_index,
                                         total_files)
                future.add_done_callback(task_done_callback)
                future_to_file[future] = file_path

                # 3. Отправляем в пул
                # future = executor.submit(parallel_worker, file_path, out_fits, overwrite, self._settings, file_index,
                #                          total_files)
                #
                # # 4. Привязываем callback, который освободит семафор, когда воркер закончит работу
                # future.add_done_callback(task_done_callback)
                #
                # future_to_file[future] = file_path

            # for file_index, file_path in enumerate(files_to_process, 1):
            #     out_fits = self._processing_controller.claim_file_for_processing(file_path, fits_files_dir)
            #     if not out_fits:
            #         continue
            #
            #     future = executor.submit(parallel_worker, file_path, out_fits, overwrite, self._settings, file_index,
            #                              total_files)
            #     future_to_file[future] = file_path

            processed_count = 0
            main_logger = logging.getLogger()
            try:
                for future in concurrent.futures.as_completed(future_to_file):
                    processed_count += 1
                    original_file = future_to_file[future]

                    # Файл завершил работу (успешно или с ошибкой). Удаляем из "висящих"
                    if original_file in claimed_files:
                        claimed_files.remove(original_file)

                    try:
                        res: WorkerResult = future.result()
                        for record in res.log_records:
                            main_logger.handle(record)

                        status = ProcessingStatus.SUCCESS if res.success else ProcessingStatus.FAILED
                        self._processing_controller.finalize_status_in_db(
                            original_file,
                            self._processing_controller.get_output_fits_pathfilename(original_file,
                                                                                     fits_files_dir) if res.success else None,
                            status,
                            res.error_msg
                        )

                    except Exception as exc:
                        logger.critical(f"FATAL Worker Crash on {original_file.name}: {exc}")
                        self._processing_controller.finalize_status_in_db(original_file, None, ProcessingStatus.FAILED,
                                                                          str(exc)[:500])
            except KeyboardInterrupt:
                logger.warning("Force termination of the process pool")
            finally:
                # =================================================================
                # 3. ОТКАТ (ROLLBACK) ДЛЯ ОТМЕНЕННЫХ ЗАДАЧ
                # =================================================================
                # Если после завершения пула в списке claimed_files остались файлы -
                # это значит, что мы их забронировали (статус PROCESSING), но задача
                # была отменена из-за Ctrl+C. Мы ОБЯЗАНЫ вернуть их в UNPROCESSED.
                if claimed_files:
                    logger.warning(f"For {len(claimed_files)} return status UNPROCESSED...")
                    for file_path in claimed_files:
                        self._processing_controller.revert_claim(file_path)

                # Мягко гасим пулл процессов, отменяя те задачи,
                # которые стояли в микро-очереди, но еще не начали выполняться
                executor.shutdown(wait=True, cancel_futures=True)


    def _parse_date(self, date_str: str) -> datetime | None:
        if not date_str:
            return None
        try:
            if len(date_str) == 8:  # Формат: 20260401
                return datetime.strptime(date_str, "%Y%m%d")
            elif len(date_str) == 15:  # Формат: 20260401_143000
                return datetime.strptime(date_str, "%Y%m%d_%H%M%S")
            else:
                raise ValueError
        except ValueError:
            logger.critical(f"Format error: '{date_str}'. Expected YYYYMMDD или YYYYMMDD_HHMMSS")
            raise

    def _find_files(self, base_dir: Path, args):
        start_dt = self._parse_date(args.start_date)

        if start_dt and not args.end_date:
            end_dt = datetime.now()
        else:
            end_dt = self._parse_date(args.end_date)

        target_dirs = []

        if args.year:
            # Если указан только год: /base_dir/YYYY
            target_dirs.append(base_dir / str(args.year))

        elif args.month:
            # Если указан месяц: /base_dir/YYYY/MM
            month_str = str(args.month)
            year, month = month_str[:4], month_str[4:]
            target_dirs.append(base_dir / year / f"{int(month):02d}")

        elif args.day:
            # Если указан день, папки дня нет, поэтому сужаем до месяца: /base_dir/YYYY/MM
            day_str = str(args.day)
            year, month = day_str[:4], day_str[4:6]
            target_dirs.append(base_dir / year / f"{int(month):02d}")

        elif start_dt and end_dt:
            # Если указан период, генерируем список папок /YYYY/MM для каждого месяца в периоде!
            curr_y, curr_m = start_dt.year, start_dt.month
            end_y, end_m = end_dt.year, end_dt.month

            while (curr_y < end_y) or (curr_y == end_y and curr_m <= end_m):
                target_dirs.append(base_dir / str(curr_y) / f"{curr_m:02d}")
                curr_m += 1
                if curr_m > 12:  # Переход на следующий год
                    curr_m = 1
                    curr_y += 1
        else:
            # Если фильтров нет (или запуск без флагов, что мы уже заблокировали в main),
            # сканируем весь архив
            target_dirs.append(base_dir)

        # Сканирование
        for target_dir in target_dirs:
            if not target_dir.exists():
                # logger.debug(f"Directory not found: {target_dir}")
                continue

            logger.debug(f"Scanning directory: {target_dir}")

            # Ищем файлы рекурсивно только внутри целевой папки
            for file_path in target_dir.rglob("*"):

                if not file_path.is_file():
                    continue

                if not self._file_filter.is_valid(file_path):
                    continue

                # Проверка нужных расширений (.bin или .bin.gz)
                # if not (file_path.name.endswith('.bin.gz') or file_path.name.endswith('.bin')):
                #     continue

                # отсеивание лишних дней/часов внутри правильной папки
                file_dateobs = self._extract_datetime_from_filename(file_path.name)
                if not file_dateobs:
                    logger.error(f"[{file_path.name}] Cannot extract datetime, skipping")
                    continue

                if args.year and file_dateobs.year != int(args.year):
                    continue

                if args.month:
                    month_str = str(args.month)
                    if file_dateobs.year != int(month_str[:4]) or file_dateobs.month != int(month_str[4:]):
                        continue

                if args.day:
                    day_str = str(args.day)
                    if (file_dateobs .year != int(day_str[:4]) or
                            file_dateobs .month != int(day_str[4:6]) or
                            file_dateobs .day != int(day_str[6:])):
                        continue

                if start_dt and file_dateobs  < start_dt:
                    continue
                if end_dt and file_dateobs  > end_dt:
                    continue

                # Файл прошел все проверки
                yield file_path

    def _extract_datetime_from_filename(self, filename: str) -> datetime | None:
        """Парсит дату и время из имени файла (например: 2025-09-01_121336_sun+00.bin.gz)"""
        # Ищем паттерн YYYY-MM-DD_HHMMSS
        match = re.search(r"(\d{4}-\d{2}-\d{2}_\d{6})", filename)
        if match:
            try:
                return datetime.strptime(match.group(1), "%Y-%m-%d_%H%M%S")
            except ValueError:
                return None
        return None

    def _handle_shutdown(self, signum, frame):
        """
            Перехват Ctrl+C
        """
        if self._shutdown_requested:
            logger.warning("Force abort! (Hard Kill)")
            exit(1)
        logger.warning("\nStop requested by user (Ctrl+C). Waiting for the current tasks to be completed...")
        self._shutdown_requested = True