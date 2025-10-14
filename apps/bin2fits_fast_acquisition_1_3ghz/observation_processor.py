from pathlib import Path

from ratan_600_data_analyzer.main import _get_output_fits_filename
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_fits_writer import \
    FastAcquisition1To3GHzFitsWriter
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import \
    FastAcquisition1To3GHzObservation
from ratan_600_data_analyzer.ratan.ratan_builder_factory import RatanBuilderFactory


class ObservationProcessor:

    @staticmethod
    def process_fast_acquisition(fast_acquisition_bin_file: Path, fits_output_path: Path):

        write_fits = True
        overwrite = True

        builder = RatanBuilderFactory.create_builder(fast_acquisition_bin_file)
        observation = None
        if RatanBuilderFactory.is_fast_1_3ghz_builder(builder):
            observation = (builder
                           .read()
                           .remove_spikes(method="kurtosis")
                           .calibrate(method="lebedev")
                           .build())

        if observation is None:
            raise Exception("No observation created")

        if isinstance(observation, FastAcquisition1To3GHzObservation):
            if write_fits:
                output_fits_file = _get_output_fits_filename(observation, fits_output_path)
                writer = FastAcquisition1To3GHzFitsWriter(observation)
                writer.write(output_fits_file, overwrite=overwrite)

    @staticmethod
    def _get_output_fits_filename(observation: FastAcquisition1To3GHzObservation, fits_output_path: Path) -> Path:

        culm_efr = observation.metadata.datetime_culmination_efrat_utc
        year = culm_efr.year
        month_str = f"{culm_efr.month:02d}"
        obs_file = observation.metadata.obs_file
        base_filename = obs_file.name.split('.', 1)[0]
        output_fits_file = Path(fits_output_path / f"{year}" / month_str / f"{base_filename}.fits")
        return output_fits_file