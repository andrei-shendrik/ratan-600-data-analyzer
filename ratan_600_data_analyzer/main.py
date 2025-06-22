from pathlib import Path

import matplotlib
from matplotlib import pyplot as plt

from ratan_600_data_analyzer.ratan.data_extractor import DataExtractor
from ratan_600_data_analyzer.ratan.polarization_type import PolarizationType
from ratan_600_data_analyzer.ratan.ratan_builder_factory import RatanBuilderFactory

def process_fast_acquisition():

    """
        todo
        __
        single_channel_data
        __
        TimeDownsampler
        FrequencyDownsampler

        pipeline Director
    """

    TIME_REDUCTION_FACTOR = 32
    FREQUENCY_REDUCTION_FACTOR = 10

    fast_acquisition_bin_file = Path(
        r"D:\data\astro\ratan-600\fast_acquisition\1-3ghz\2024\08\2024-08-01_121957_sun+00.bin")

    fast_acq_fits_file = Path(
        r"D:\data\astro\ratan-600\fast_acquisition\1-3ghz\fits\2024\08\2024-08-01_121957_sun+00.fits")

    output_fits_file = Path(
        r"D:\data\astro\ratan-600\fast_acquisition\1-3ghz\fits\2024\08\2024-08-01_121957_sun+00_out.fits")

    builder = RatanBuilderFactory.create_builder(fast_acquisition_bin_file)
    observation = None
    if RatanBuilderFactory.is_fast_1_3ghz_builder(builder):
        observation = (builder
                       .read()
                       # .remove_spikes(method="kurtosis")
                       # .interpolate_gaps(method="linear")
                       # .time_downsample(TIME_REDUCTION_FACTOR)
                       .build())

        # .remove_data(kurtosis)
        # .frequency_downsample(FREQUENCY_REDUCTION_FACTOR)
        # .calibrate(method="components")
        # .write(".fits", output_fits_file)
    if observation is None:
        raise Exception("No observation created")

    # writer = FitsWriter(observation)
    # output_fits_file = Path(r"D:\data\astro\ratan-600\fast_acquisition\1-3ghz\fits\2024\08\2024-08-01_121957_sun+00.fits")
    # writer.save(output_fits_file)

    print(observation.metadata.polarizations)
    print(f"Dateobs: {observation.metadata.datetime_culmination_utc}")

    # print(type(sspc_obs.metadata))

    data_extractor = DataExtractor(observation)

    target_freq = 15.0
    pol = PolarizationType.LHCP

    # freq = 1.5 # !!!
    # freq = 2.7 # !!!
    # pol = PolarizationType.LHCP

    channel_data = data_extractor.get_channel_data(target_freq, pol)
    print(f"Freq: {channel_data.frequency} Pol: {channel_data.polarization.value}")
    print(channel_data.array)

    # figure
    matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'

    # window
    plt.figure()

    plt.plot(channel_data.array)
    plt.xlabel("")
    plt.ylabel("")
    plt.suptitle(f"{observation.metadata.datetime_culmination_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC", fontsize=12)
    plt.text(0.5, 1.02, f"{channel_data.frequency:.2f} GHz; {channel_data.polarization.value}", ha="center",
             va="bottom", fontsize=12,
             transform=plt.gca().transAxes)

    # window1
    # plt.figure()
    #
    # plt.plot(channel_data2)
    # plt.xlabel("")
    # plt.ylabel("")
    # plt.suptitle(f"{culm2_utc_formatted} UTC", fontsize=12)
    # plt.text(0.5, 1.02, f"{frequency2:.2f} GHz; {data_type}", ha="center", va="bottom", fontsize=12, transform=plt.gca().transAxes)

    # показ всех графиков
    plt.show()

    # scan_plotter = ScanPlotter()
    # scan_plotter.add_series(observation, freq, pol)
    # scan_plotter.show()

    # scan_plotter.set_title("")
    # scan_plotter.set_size(1024,1024)
    # scan_plotter.save(file)

    # writer = FitsWriter(observation)
    # output_fits_file = Path(r"D:\data\astro\ratan-600\fast_acquisition\1-3ghz\fits\2024\08\2024-08-01_121957_sun+00.fits")
    # writer.save(output_fits_file)

def process_sspc():
    sspc_fits_file = Path(r"D:\data\astro\ratan-600\sun\fits\level1\2017\09\20170905_121217_sun+0.fits")

    builder = RatanBuilderFactory.create_builder(sspc_fits_file)
    observation = None
    if RatanBuilderFactory.is_sspc_builder(builder):
        observation = (builder
                       .read()
                       .build())
    if observation is None:
        raise Exception("No observation created")

    print(observation.metadata.polarizations)
    print(f"Dateobs: {observation.metadata.datetime_culmination_utc}")

    data_extractor = DataExtractor(observation)

    target_freq = 15.0
    pol = PolarizationType.LHCP

    # freq = 1.5 # !!!
    # freq = 2.7 # !!!
    # pol = PolarizationType.LHCP

    channel_data = data_extractor.get_channel_data(target_freq, pol)
    print(f"Freq: {channel_data.frequency} Pol: {channel_data.polarization.value}")
    print(channel_data.array)

    # figure
    matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'

    # window
    plt.figure()

    plt.plot(channel_data.array)
    plt.xlabel("")
    plt.ylabel("")
    plt.suptitle(f"{observation.metadata.datetime_culmination_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC", fontsize=12)
    plt.text(0.5, 1.02, f"{channel_data.frequency:.2f} GHz; {channel_data.polarization.value}", ha="center",
             va="bottom", fontsize=12,
             transform=plt.gca().transAxes)
    plt.show()


def main():
    # process_sspc()
    process_fast_acquisition()

if __name__ == "__main__":
  main()
