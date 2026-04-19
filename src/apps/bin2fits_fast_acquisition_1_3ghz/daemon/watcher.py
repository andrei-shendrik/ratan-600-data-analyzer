import logging
import os
import time
from datetime import datetime
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from apps.bin2fits_fast_acquisition_1_3ghz.services.observation_file_filter import ObservationFileFilter

logger = logging.getLogger(__name__)


class BinFileEventHandler(FileSystemEventHandler):
    def __init__(self, processing_controller, settings):
        self._processing_controller = processing_controller
        self._settings = settings
        self._file_filter = ObservationFileFilter(self._settings.file_filters)

    def _wait_for_file_to_finish_writing(self, file_path: str, wait_time: int = 2, retries: int = 5) -> bool:
        """
        Проверяет, что файл полностью записан на диск, сравнивая его размер.
        Возвращает True, если файл готов к чтению.
        """
        previous_size = -1
        for _ in range(retries):
            try:
                current_size = os.path.getsize(file_path)
                if current_size == previous_size and current_size > 0:
                    return True  # Размер перестал меняться, файл записан
                previous_size = current_size
                time.sleep(wait_time)
            except OSError:
                time.sleep(wait_time)  # Файл мог быть временно заблокирован
        return False

    def on_moved(self, event):
        # Событие от rsync (переименование из .temp в .bin.gz)
        dest_path = Path(os.fsdecode(event.dest_path))
        if self._file_filter.is_valid(dest_path):
            logger.info(f"Watcher: detected new file (moved): {dest_path}")
            self._processing_controller.process_file(
                bin_file=dest_path,
                fits_base_dir=self._settings.fits_archive
            )

    def on_created(self, event):
        # Событие от cp / ftp (создание нового файла)
        src_path_str = os.fsdecode(event.src_path)
        src_path = Path(src_path_str)

        if not event.is_directory and self._file_filter.is_valid(src_path):
            logger.info(f"Watcher: detected new file (created): {src_path}")

            if self._wait_for_file_to_finish_writing(src_path_str):
                self._processing_controller.process_file(
                    bin_file=src_path,
                    fits_base_dir=self._settings.fits_archive
                )
            else:
                logger.error(f"Watcher: timeout waiting for file to finish writing: {src_path_str}")


class Watcher:
    def __init__(self, processing_controller, settings):
        self._settings = settings
        self._base_dir = settings.bin_archive.resolve()
        self._event_handler = BinFileEventHandler(processing_controller, settings)
        self._observer = Observer()

        # Словарь для хранения текущих активных подписок: { 'путь_к_папке': объект_watch }
        self._active_watches = {}

    def _get_target_directories(self) -> list[Path]:
        """
        Вычисляет пути для текущего и предыдущего месяцев (YYYY/MM).
        """
        now = datetime.now()
        curr_year, curr_month = now.year, now.month

        # Логика перехода через год для предыдущего месяца
        if curr_month == 1:
            prev_year, prev_month = curr_year - 1, 12
        else:
            prev_year, prev_month = curr_year, curr_month - 1

        curr_dir = self._base_dir / str(curr_year) / f"{curr_month:02d}"
        prev_dir = self._base_dir / str(prev_year) / f"{prev_month:02d}"

        return [curr_dir, prev_dir]

    def _update_watches(self):
        """
        Сверяет целевые директории с теми, которые сейчас отслеживаются.
        Добавляет новые и удаляет устаревшие подписки (переход месяца).
        """
        # Получаем список путей, которые мы ХОТИМ отслеживать (и они физически существуют!)
        target_dirs = self._get_target_directories()
        target_paths = [str(d) for d in target_dirs if d.exists()]

        current_paths = list(self._active_watches.keys())

        # 1. Отписываемся от старых месяцев (которых больше нет в target_paths)
        for path in current_paths:
            if path not in target_paths:
                watch = self._active_watches[path]
                self._observer.unschedule(watch)
                del self._active_watches[path]
                logger.info(f"Watcher: disabling monitoring directory: {path}")

        # 2. Подписываемся на новые месяцы (если их еще нет в активных)
        for path in target_paths:
            if path not in self._active_watches:
                watch = self._observer.schedule(self._event_handler, path, recursive=True)
                self._active_watches[path] = watch
                logger.info(f"Watcher: starting monitoring directory: {path}")

    def start(self):
        logger.info(f"Watcher bin2fits_fast_1_3 has started")
        self._observer.start()

        try:
            # Бесконечный цикл жизни демона
            while True:
                # Раз в 10 минут проверка, не сменился ли месяц
                # и не появились ли нужные папки на диске
                self._update_watches()
                time.sleep(600)

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        logger.info("Stopping Watcher...")
        self._observer.stop()
        self._observer.join()