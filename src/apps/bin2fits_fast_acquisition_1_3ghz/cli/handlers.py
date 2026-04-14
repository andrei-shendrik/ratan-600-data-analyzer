import os
import re
from datetime import datetime
from pathlib import Path

from ratan_600_data_analyzer.logging.logger_configurator import get_logger

logger = get_logger(__name__)


class CliBatchHandler:
    def __init__(self, obs_processor, settings):
        self._obs_processor = obs_processor
        self._settings = settings

    def execute(self, args):
        bin_files_dir = Path(args.bin_dir).resolve() if args.bin_dir else self._settings.bin_archive.resolve()
        fits_files_dir = Path(args.fits_dir).resolve() if args.fits_dir else self._settings.fits_archive.resolve()

        if not bin_files_dir.exists():
            logger.error(f"Bin dir doesnt exist: {bin_files_dir}")
            return

        # Обработка одиночного файла (--file)
        if args.file:
            target_file = Path(args.file).resolve()
            if target_file.exists():
                self._obs_processor.process_file(
                    bin_file=target_file,
                    fits_base_dir=fits_files_dir,
                    overwrite=args.overwrite,
                    retry_failed=args.failed
                )
            else:
                logger.error(f"Specified .bin file not found: {target_file}")
            return

        # Пакетная обработка (поиск файлов)
        logger.info(f"Search for .bin files in directory: {bin_files_dir}")
        files_to_process = list(self._find_files(bin_files_dir, args))
        total_files = len(files_to_process)

        if total_files == 0:
            logger.info("Files not found")
            return

        logger.info(f".bin files found: {total_files}")

        # Запуск конвеера
        success_count = 0
        for i, file_path in enumerate(files_to_process, 1):
            logger.info(f"--- [Processing {i} of {total_files}] --- : {file_path}")

            # process_file внутри себя ловит ошибки, поэтому цикл не прервется
            self._obs_processor.process_file(
                bin_file=file_path,
                fits_base_dir=fits_files_dir,
                overwrite=args.overwrite,
                retry_failed=args.failed
            )
            success_count += 1

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

                # Проверка нужных расширений (.bin или .bin.gz)
                if not (file_path.name.endswith('.bin.gz') or file_path.name.endswith('.bin')):
                    continue

                # 3. ТОЧЕЧНАЯ ФИЛЬТРАЦИЯ (для отсеивания лишних дней/часов внутри правильной папки)
                file_dateobs = self._extract_datetime_from_filename(file_path.name)
                if not file_dateobs:
                    raise

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