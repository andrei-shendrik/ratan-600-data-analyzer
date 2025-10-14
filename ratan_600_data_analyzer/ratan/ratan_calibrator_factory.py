from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_calibrator_lebedev import \
    FastAcquisition1To3GHzCalibratorLebedev
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import \
    FastAcquisition1To3GHzObservation
from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation
from ratan_600_data_analyzer.ratan.ratan_observation_calibrator import RatanObservationCalibrator

class RatanCalibratorFactory:

    @staticmethod
    def create_calibrator(observation: RatanObservation, calibration_method: str) -> RatanObservationCalibrator:

        if isinstance(observation, FastAcquisition1To3GHzObservation):
            if calibration_method.lower() == "lebedev":
                calibrator = FastAcquisition1To3GHzCalibratorLebedev(observation)
                return calibrator
            else:
                raise ValueError(f"No calibration method found: {calibration_method}")
        raise ValueError(f"No suitable calibrator found for observation: {observation.metadata.file}")