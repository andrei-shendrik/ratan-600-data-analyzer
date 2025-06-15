from typing import Tuple, List

import numpy as np
from matplotlib import pyplot as plt

from ratan_600_data_analyzer.ratan.data_extractor import DataExtractor
from ratan_600_data_analyzer.ratan.polarization_type import PolarizationType


class ScanPlotter:
    def __init__(self):
        self._series: List[dict] = []  # Хранилище данных серий
        self._title: str = "Scan"
        self._figure_size: Tuple[int, int] = (10, 6)
        self._xlabel: str = "x"
        self._ylabel: str = "y"
        self._colors: List[str] = ['blue', 'orange', 'green', 'red', 'purple']
        self._current_style_index: int = 0

    def set_title(self, title: str):
        self._title = title

    def set_labels(self, xlabel: str, ylabel: str):
        self._xlabel = xlabel
        self._ylabel = ylabel

    def set_size(self, width: int, height: int):
        self._figure_size = (width, height)

    def add_series(self, observation, freq: float, pol: PolarizationType):
        data_extractor = DataExtractor(observation)
        data = data_extractor.get_channel_data(freq, pol).array

        label = f"Freq: {freq} GHz, Pol: {pol.name}"

        self._series.append({
            'data': data,
            'label': label,
            'color': self._colors[self._current_style_index % len(self._colors)],
        })
        self._current_style_index += 1

    def show(self):
        plt.figure(figsize=self._figure_size)

        for series in self._series:
            time_axis = np.arange(len(series['data']))
            plt.plot(
                time_axis,
                series['data'],
                label=series['label'],
                color=series['color'],
                linewidth=1.5
            )

        plt.title(self._title)
        plt.xlabel(self._xlabel)
        plt.ylabel(self._ylabel)
        plt.grid(True)

        if any(series['label'] for series in self._series):
            plt.legend()

        plt.tight_layout()
        plt.show()

    def save(self, filename: str, dpi: int = 300):

        plt.figure(figsize=self._figure_size)

        for series in self._series:
            time_axis = np.arange(len(series['data']))
            plt.plot(
                time_axis,
                series['data'],
                label=series['label'],
                color=series['color'],
                linestyle=series['linestyle'],
                linewidth=1.5
            )

        plt.title(self._title)
        plt.xlabel(self._xlabel)
        plt.ylabel(self._ylabel)
        plt.grid(True)

        if any(series['label'] for series in self._series):
            plt.legend()

        plt.tight_layout()
        plt.savefig(filename, dpi=dpi, bbox_inches='tight')
        plt.close()