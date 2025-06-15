from pathlib import Path

from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_factory import \
    FastAcquisition1To3GHzFactory
from ratan_600_data_analyzer.ratan.ratan_observation_processor import RatanObservationProcessor


class FastAcquisition1To3GHzProcessor(RatanObservationProcessor):
    def __init__(self, file: Path):
        super().__init__(file)

    def process(self, file: Path):
        factory = FastAcquisition1To3GHzFactory()
        reader = factory.create_reader(file)
        calibrator = factory.create_calibrator()

        observation = reader.read(file)
        calibrator.calibrate(observation)
        return observation

    def save_to_file(self, file: Path):
        pass