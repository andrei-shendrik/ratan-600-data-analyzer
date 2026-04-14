import time
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from src.ratan_600_data_analyzer.logging.logger_configurator import get_logger

logger = get_logger(__name__)

class BinFileEventHandler(FileSystemEventHandler):

    def __init__(self, obs_processor):
        self._obs_processor = obs_processor

    def on_moved(self, event):
        # rsync temp file rename
        if event.dest_path.endswith('.bin'):
            logger.info(f"Watchdog: found new .bin file: {event.dest_path}")
            self._obs_processor.process_single_file(Path(event.dest_path))

    def on_created(self, event):
        # На случай ручного копирования (cp) или Windows
        if event.src_path.endswith('.bin') and not event.is_directory:
            logger.info(f"Watchdog: Обнаружен новый скопированный файл -> {event.src_path}")
            self._obs_processor.process_single_file(Path(event.src_path))


class Watcher:

    def __init__(self, obs_processor, watch_dir: Path):
        self._watch_dir = str(watch_dir)
        self._event_handler = BinFileEventHandler(obs_processor)
        self._observer = Observer()

    def start(self):
        logger.info(f"Watchdog has been started. Watching for directory: {self._watch_dir}")
        # schedule настраивает наблюдателя на конкретную папку рекурсивно
        self._observer.schedule(self._event_handler, self._watch_dir, recursive=True)
        self._observer.start()

        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        logger.info("Stopping Watchdog...")
        self._observer.stop()
        self._observer.join()