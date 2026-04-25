import concurrent.futures
import logging
import re
import signal
from datetime import datetime
from pathlib import Path

from apps.bin2fits_fast_acquisition_1_3ghz.infrastructure.database import ProcessingStatus
from apps.bin2fits_fast_acquisition_1_3ghz.services.observation_file_filter import ObservationFileFilter
from apps.bin2fits_fast_acquisition_1_3ghz.services.observation_processor import \
    FastAcquisition1To3GHzObservationProcessor
from apps.bin2fits_fast_acquisition_1_3ghz.services.parallel_worker import WorkerResult, parallel_worker, init_worker
from apps.bin2fits_fast_acquisition_1_3ghz.services.process_profiler import ProcessProfiler

logger = logging.getLogger(__name__)


class CliBatchHandler:
    def __init__(self, processing_controller, settings):
        self._max_recorded_ram_mb = None
        self._processing_controller = processing_controller
        self._settings = settings
        self._file_filter = ObservationFileFilter(self._settings.file_filters)

        self._shutdown_requested = False
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def execute(self, args):
        with ProcessProfiler() as batch_profiler:
            self._max_recorded_ram_mb = 0.0
            
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

            mode = f"parallel ({active_workers} workers)" if is_multi_processing else "single-processing (1 worker)"
            logger.info(f"Starting processing of {num_files_to_process} files in {mode} mode...")

            if not is_multi_processing:
                self._run_sequential(files_to_process, fits_files_dir, args.overwrite, num_files_to_process)
            else:
                logger.info(f"Please wait for processes messages...")
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

            logger.info(f"Total Task Time      : {batch_profiler.formatted_time}")
            logger.info(f"Peak RAM used by Worker  : {self._max_recorded_ram_mb:.1f} MB")

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
                with ProcessProfiler() as profiler:
                    FastAcquisition1To3GHzObservationProcessor.execute(file_path, out_fits, overwrite)
                success = True
                logger.info(
                    f"[{filename}] Stats -> Time: {profiler.formatted_time} | Peak RAM: {profiler.peak_memory_mb:.1f} MB")
                if profiler.peak_memory_mb > self._max_recorded_ram_mb:
                    self._max_recorded_ram_mb = profiler.peak_memory_mb
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

        claimed_files = set()
        future_to_file = {}
        pending_futures = set()

        file_iterator = iter(enumerate(files_to_process, 1))
        max_in_queue = active_workers * 2
        processed_count = 0
        main_logger = logging.getLogger()

        max_ram_limit = self._settings.resources.worker_max_ram_gb

        with concurrent.futures.ProcessPoolExecutor(
                max_workers=active_workers,
                initializer=init_worker,
                initargs=(max_ram_limit,)) as executor:

            def submit_next_tasks():
                if self._shutdown_requested:
                    return

                while len(pending_futures) < max_in_queue:
                    try:
                        # ИЗМЕНЕНО: Имена переменных сделаны специфичными для этой функции
                        task_index, task_file_path = next(file_iterator)
                    except StopIteration:
                        break

                    out_fits = self._processing_controller.claim_file_for_processing(task_file_path, fits_files_dir)
                    if not out_fits:
                        continue

                    claimed_files.add(task_file_path)

                    # ИЗМЕНЕНО: Назвали переменную new_future
                    new_future = executor.submit(parallel_worker, task_file_path, out_fits, overwrite, self._settings,
                                                 task_index, total_files)

                    # ИЗМЕНЕНО: Используем новые имена переменных
                    future_to_file[new_future] = task_file_path
                    pending_futures.add(new_future)

            # 1. ПЕРВИЧНОЕ ЗАПОЛНЕНИЕ ОЧЕРЕДИ
            submit_next_tasks()

            # 2. ГЛАВНЫЙ ЦИКЛ
            try:
                while pending_futures:
                    # ИЗМЕНЕНО: done переименовано в done_futures для ясности
                    done_futures, pending_futures = concurrent.futures.wait(
                        pending_futures,
                        timeout=1.0,
                        return_when=concurrent.futures.FIRST_COMPLETED
                    )

                    if self._shutdown_requested:
                        logger.warning(
                            "Loop interruption: new files will not be processed. Waiting for running tasks to finish...")

                    # ИЗМЕНЕНО: Переменная цикла теперь completed_future
                    for completed_future in done_futures:
                        processed_count += 1
                        original_file = future_to_file[completed_future]

                        if original_file in claimed_files:
                            claimed_files.remove(original_file)

                        try:
                            # ИЗМЕНЕНО: Вызов результата из completed_future
                            res: WorkerResult = completed_future.result()

                            if res.peak_memory_mb > self._max_recorded_ram_mb:
                                self._max_recorded_ram_mb = res.peak_memory_mb

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
                            self._processing_controller.finalize_status_in_db(original_file, None,
                                                                              ProcessingStatus.FAILED, str(exc)[:500])

                    # 3. ДОКИДЫВАЕМ НОВЫЕ ЗАДАЧИ ВМЕСТО ЗАВЕРШЕННЫХ
                    if not self._shutdown_requested:
                        submit_next_tasks()

            except KeyboardInterrupt:
                logger.warning("Force termination of the process pool")
            finally:
                # 4. ОТКАТ (ROLLBACK) ДЛЯ ОТМЕНЕННЫХ ЗАДАЧ
                if claimed_files:
                    logger.warning(f"For {len(claimed_files)} files returning status UNPROCESSED...")
                    for file_path in claimed_files:
                        self._processing_controller.revert_claim(file_path)

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