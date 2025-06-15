import copy
from pathlib import Path

import numpy as np
from astropy.io import fits

from ratan_600_data_analyzer.logger.logger import logger
from ratan_600_data_analyzer.observation.observation_reader import ObservationReader
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_metadata import FastAcquisition1To3GHzMetadata
from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation


class FastAcquisition1To3GHzFitsReader(ObservationReader):

    def can_read(self, file: Path) -> bool:
        if not file.suffix.lower() == '.fits':
            return False
            # try:
            #
            # except Exception:
            #     return False
        return True

    def read(self, file: Path):
        try:
            with fits.open(file) as hdul:
                header = copy.deepcopy(hdul[0].header)
                header2 = copy.deepcopy(hdul[1].data)
                data = copy.deepcopy(hdul[0].data.astype(np.float32))
        except (FileNotFoundError, OSError, ValueError) as e:
            message = f"Error while reading file: {file}"
            logger.exception(f"{message}")
            raise IOError(f"{message}: {e}") from e

        #fast_acquisition_metadata = FastAcquisitionMetadata.create_from_fits(header, header2, data)
        #observation = RatanObservation(fast_acquisition_metadata, data)
        #return observation
        pass

    def read_metadata(self, file_path: Path):
        pass