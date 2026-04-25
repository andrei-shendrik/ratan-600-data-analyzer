import sys
import time

import psutil


class ProcessProfiler:
    """
    Контекстный менеджер для замера времени выполнения
    и пикового потребления памяти (RAM) текущим процессом.
    """
    def __init__(self):
        self.start_time = 0.0
        self.end_time = 0.0
        self.elapsed_seconds = 0.0
        self.peak_memory_mb = 0.0
        # Запоминаем текущий процесс
        self._process = psutil.Process()

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.elapsed_seconds = self.end_time - self.start_time

        # Получаем пиковое потребление памяти
        if sys.platform != 'win32':
            # На Linux/UNIX встроенный модуль resource делает это идеально (возвращает в Килобайтах)
            import resource
            usage = resource.getrusage(resource.RUSAGE_SELF)
            self.peak_memory_mb = usage.ru_maxrss / 1024.0
        else:
            # На Windows ru_maxrss не работает. Используем psutil для получения пика памяти (Peak Working Set)
            memory_info = self._process.memory_info()
            # В Windows атрибут peak_wset хранит пиковое значение в байтах
            if hasattr(memory_info, 'peak_wset'):
                self.peak_memory_mb = memory_info.peak_wset / (1024 * 1024)
            else:
                # Fallback, если атрибута нет (просто текущая память)
                self.peak_memory_mb = memory_info.rss / (1024 * 1024)

    @property
    def formatted_time(self) -> str:
        """Возвращает время в формате ЧЧ:ММ:СС"""
        m, s = divmod(int(self.elapsed_seconds), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h}h {m}m {s}s"
        return f"{m}m {s}s"