

class ObservationProcessingFacade:
    # RatanObservationProcessor

    """
    Facade
    """
    # def __init__(self):
    #     self.observation = None
    #
    # def read_observation(self, file_path: str):
    #     reader = ReaderFactory.get_reader(file_path)
    #     self.observation = reader.read_inplace(file_path)
    #
    # def denoise_observation(self):
    #     denoiser = DenoiserFactory.get_denoiser(self.observation)
    #     denoiser.denoise_inplace(self.observation)
    #
    # def calibrate_observation(self, method: str):
    #     calibrator = CalibratorFactory.get_calibrator(method, self.observation)
    #     calibrator.calibrate_inplace(self.observation)
    #
    # def find_sun_center(self):
    #     finder = SunCenterFinderFactory.get_finder(self.observation)
    #     finder.find_center_inplace(self.observation)
    #
    # def downsample_observation(self):
    #     if isinstance(self.observation, FastAcquisitionObservation):
    #         downsampler = DownsamplerFactory.get_downsampler(self.observation)
    #         downsampler.downsample_inplace(self.observation)
    #
    # def save_observation(self, output_path: str):
    #     saver = SaverFactory.get_saver(output_path)
    #     saver.save_inplace(self.observation, output_path)