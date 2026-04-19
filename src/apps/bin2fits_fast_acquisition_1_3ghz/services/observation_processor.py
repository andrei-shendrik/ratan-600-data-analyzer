import logging
from pathlib import Path

from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_fits_writer import \
    FastAcquisition1To3GHzFitsWriter
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import \
    FastAcquisition1To3GHzObservation
from ratan_600_data_analyzer.ratan.ratan_builder_factory import RatanBuilderFactory

logger = logging.getLogger(__name__)

class FastAcquisition1To3GHzObservationProcessor:
    """
        Обработка наблюдения
    """
    @staticmethod
    def execute(bin_file: Path, output_fits_file: Path, overwrite: bool) -> None:
        logger.info(f"[{bin_file.name}] Started processing")

        builder = RatanBuilderFactory.create_builder(bin_file)
        if not RatanBuilderFactory.is_fast_1_3ghz_builder(builder):
            raise ValueError(f"Invalid builder type for file {bin_file.name}")

        observation = (builder.read()
                       .remove_spikes(method="kurtosis")
                       .calibrate(method="lebedev")
                       .build())

        if observation is None:
            raise RuntimeError("Processing failed: no observation created")

        if isinstance(observation, FastAcquisition1To3GHzObservation):
            writer = FastAcquisition1To3GHzFitsWriter(observation)
            writer.write(output_fits_file, overwrite)
            logger.info(f"[{bin_file.name}] Successfully converted to '{output_fits_file}'")
        else:
            raise TypeError("Processing failed: Invalid observation type returned")