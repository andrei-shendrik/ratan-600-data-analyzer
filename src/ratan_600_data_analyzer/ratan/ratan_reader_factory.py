from pathlib import Path
from typing import List, Type

from src.ratan_600_data_analyzer.observation.observation_reader import ObservationReader
from src.ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_bin_reader import \
    FastAcquisition1To3GHzBinReader
from src.ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_fits_reader import \
    FastAcquisition1To3GHzFitsReader
from src.ratan_600_data_analyzer.ratan.ratan_observation_reader import RatanObservationReader
from src.ratan_600_data_analyzer.ratan.sspc.sspc_fits_reader import SSPCFitsReader


class RatanReaderFactory:

    READER_CLASSES: List[Type[RatanObservationReader]] = [
        SSPCFitsReader,
        FastAcquisition1To3GHzBinReader,
        FastAcquisition1To3GHzFitsReader
    ]

    @staticmethod
    def create_reader(file: Path) -> ObservationReader:

        for reader_class in RatanReaderFactory.READER_CLASSES:
            reader = reader_class()
            if reader.can_read(file):
                return reader
        raise ValueError(f"No suitable reader found for file: {file}")