import copy
import time
from datetime import datetime
from pathlib import Path

import matplotlib
import numpy as np
from astropy.io import fits
from matplotlib import pyplot as plt

from ratan_600_data_analyzer.ratan.data_extractor import DataExtractor
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_configuration import \
    config
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_fits_writer import \
    FastAcquisition1To3GHzFitsWriter
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import \
    FastAcquisition1To3GHzObservation
from ratan_600_data_analyzer.ratan.polarization_type import PolarizationType
from ratan_600_data_analyzer.ratan.ratan_builder_factory import RatanBuilderFactory

FITS_OUTPUT_PATH = Path(r"D:\data\astro\ratan-600\fast_acquisition\1-3ghz\fits")

def time_counter(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs) # Выполняем саму функцию
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"'{func.__name__}' execution time {execution_time:.4f} sec")
        return result
    return wrapper

def process_observations():

    """
    config_loader
    data_loader
    """

    # fast_acquisition_bin_file = Path(
    #     r"D:\data\astro\ratan-600\fast_acquisition\1-3ghz\bin\2024\08\2024-08-01_121957_sun+00.bin.gz")

    fast_acquisition_bin_file = Path(
        r"D:\data\astro\ratan-600\fast_acquisition\1-3ghz\bin\2025\09\2025-09-01_121336_sun+00.bin.gz")


    # fast_acquisition_bin_file = Path(
    #          r"D:\data\astro\ratan-600\fast_acquisition\1-3ghz\2025\03\2025-03-21_122043_Sun+00.bin.gz")

    # fast_acq_fits_file = Path(
    #     r"D:\data\astro\ratan-600\fast_acquisition\1-3ghz\fits\2024\08\2024-08-01_121957_sun+00.fits")

    output_fits_file = process_fast_acquisition(fast_acquisition_bin_file, FITS_OUTPUT_PATH)
    #read_fits(output_fits_file)

@time_counter
def process_fast_acquisition(fast_acquisition_bin_file: Path, fits_output_path: Path) -> Path:

    """
        single_channel_data
        __
        TimeDownsampler
        FrequencyDownsampler
        pipeline Director
    """
    write = True
    builder = RatanBuilderFactory.create_builder(fast_acquisition_bin_file)
    observation = None
    if RatanBuilderFactory.is_fast_1_3ghz_builder(builder):
        observation = (builder
                        .read()
                        .remove_spikes(method="kurtosis")
                        .calibrate(method="lebedev")
                        .build())

        # available
        # .write(".fits", output_fits_file)
        # .interpolate_gaps(method="linear")
        # .time_downsample(time_reduction_factor=16)

        # potential adding
        # .empty_raw_data() .remove_data("kurtosis")
        # .frequency_downsample(FREQUENCY_REDUCTION_FACTOR)

    if observation is None:
        raise Exception("No observation created")

    if isinstance(observation, FastAcquisition1To3GHzObservation):
        _print_header_params(observation)

        # write fits
        if write:
            overwrite = True
            output_fits_file = _get_output_fits_filename(observation, fits_output_path)
            writer = FastAcquisition1To3GHzFitsWriter(observation)
            writer.write(output_fits_file, overwrite=overwrite)

            lhcp = observation.data.lhcp
            rhcp = observation.data.rhcp
            data_cube_bin = np.stack([lhcp, rhcp], axis=1)
            data_cube_fits = read_fits(output_fits_file)
            bin_arr = data_cube_bin[0,0,:]
            fits_arr = data_cube_fits[0, 0, :]
            print(f"Bin {data_cube_bin.shape}")
            print(f"Fits {data_cube_bin.shape}")

            are_equal = np.array_equal(data_cube_bin, data_cube_fits)
            print(f"Are equal {are_equal}")

            #test
            # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
            # plt.figure(figsize=(18, 10))  # Создаем фигуру размером 12x6 дюймов
            #
            # # Рисуем первый массив
            # plt.plot(bin_arr , label='Bin', color='blue', linewidth=1.5)
            #
            # # Рисуем второй массив на той же фигуре
            # plt.plot(fits_arr, label='Fits', color='red', linestyle='--', linewidth=1)
            #
            # # Добавляем элементы для наглядности
            # plt.title('Сравнение массивов для частоты [0] и поляризации [0]')
            # plt.xlabel('Индекс отсчета')
            # plt.ylabel('Амплитуда')
            # plt.legend()  # Показывает метки 'Массив 1' и 'Массив 2'
            # plt.grid(True)  # Включаем сетку
            # plt.tight_layout()  # Оптимизируем поля
            # #plt.show()

            #test2
            difference_data = data_cube_bin - data_cube_fits
            difference = difference_data[0, 0, :]

            # 3. Строим график разницы
            # plt.figure(figsize=(12, 6))
            #
            # plt.plot(difference, label='Diff', color='green')
            #
            # # Добавим горизонтальную линию на уровне нуля для наглядности
            # plt.axhline(0, color='black', linestyle='--', linewidth=0.8, label='Нулевой уровень')
            #
            # # Добавляем элементы
            # plt.title('Разница между массивами для частоты [0] и поляризации [0]')
            # plt.xlabel('Индекс отсчета')
            # plt.ylabel('Разница амплитуд')
            # plt.legend()
            # plt.grid(True)
            # plt.tight_layout()

            # Показываем график
            #plt.show()

            mean_diff = np.mean(difference)
            std_diff = np.std(difference)
            max_diff = np.max(difference)
            min_diff = np.min(difference)

            print("\n--- Статистика разницы ---")
            print(f"Среднее значение разницы: {mean_diff:.16f}")
            print(f"Стандартное отклонение разницы: {std_diff:.16f}")
            print(f"Максимальная разница: {max_diff:.16f}")
            print(f"Минимальная разница: {min_diff:.16f}")

            return output_fits_file

        #test3
        # start_index = 10000
        # end_index = 10100
        #
        # # Извлекаем срезы в этом диапазоне
        # x_axis = np.arange(start_index, end_index)
        # data1_zoom = data_cube_bin[0, 0, start_index:end_index]
        # data2_zoom = data_cube_fits[0, 0, start_index:end_index]
        # diff_zoom = data2_zoom - data1_zoom
        #
        # # --- Создаем комплексный график: сравнение + разница ---
        # fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
        #
        # # Верхний график: Сравнение сигналов точками
        # # Используем plt.plot с маркерами, это очень быстро
        # ax1.plot(x_axis, data1_zoom, linestyle='none', marker='.', markersize=4, label='Массив 1 (точки)')
        # ax1.plot(x_axis, data2_zoom, linestyle='none', marker='.', markersize=4, label='Массив 2 (точки)',
        #          alpha=0.5)  # alpha - прозрачность
        # ax1.set_title(f'Детальное сравнение точками (участок {start_index}-{end_index})')
        # ax1.set_ylabel('Амплитуда')
        # ax1.legend()
        # ax1.grid(True)
        #
        # # Нижний график: Разница
        # ax2.plot(x_axis, diff_zoom, linestyle='none', marker='o', markersize=3, color='green')
        # ax2.axhline(0, color='black', linestyle='--', linewidth=0.8)
        # ax2.set_title('Разница на детальном участке')
        # ax2.set_xlabel(f'Индекс отсчета (смещение {start_index})')
        # ax2.set_ylabel('Разница')
        # ax2.grid(True)
        #
        # plt.tight_layout()
        # plt.show()


        #figure
        # data = observation.data
        # lhcp = data.lhcp
        # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
        # plt.figure(figsize=(14, 8))
        # for freq_idx in range(lhcp.shape[0]):
        #     plt.plot(lhcp[freq_idx, :],
        #             alpha=0.5,
        #             linewidth = 1,
        #             marker = 'o',
        #             markersize = 2
        #     )
        # plt.grid(alpha=0.3)
        # plt.tight_layout()
        # plt.show()



    #data_extractor = DataExtractor(observation)
    #target_freq = 2.0
    #pol = PolarizationType.LHCP

    # freq = 1.5 # !!!
    # freq = 2.7 # !!!
    # pol = PolarizationType.LHCP

    #channel_data = data_extractor.get_channel_data(target_freq, pol)
    #print(f"Freq: {channel_data.frequency} Pol: {channel_data.polarization.value}")

    # figure
    # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
    #
    # # window
    # plt.figure(figsize=(14, 8))
    # plt.plot(channel_data.array,
    #          linewidth=1,
    #          marker='o',
    #          markersize=2,
    #          )
    # plt.xlabel("")
    # plt.ylabel("")
    # plt.suptitle(f"{observation.metadata.datetime_culmination_feed_horn_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC", fontsize=12)
    # plt.text(0.5, 1.02, f"{channel_data.frequency:.2f} GHz; {channel_data.polarization.value}", ha="center",
    #          va="bottom", fontsize=12,
    #          transform=plt.gca().transAxes)

    # window1
    # plt.figure()
    #
    # plt.plot(channel_data2)
    # plt.xlabel("")
    # plt.ylabel("")
    # plt.suptitle(f"{culm2_utc_formatted} UTC", fontsize=12)
    # plt.text(0.5, 1.02, f"{frequency2:.2f} GHz; {data_type}", ha="center", va="bottom", fontsize=12, transform=plt.gca().transAxes)

    # показ всех графиков
    #plt.show()

    # scan_plotter = ScanPlotter()
    # scan_plotter.add_series(observation, freq, pol)
    # scan_plotter.show()

    # scan_plotter.set_title("")
    # scan_plotter.set_size(1024,1024)
    # scan_plotter.save(file)

    # writer = FitsWriter(observation)
    # output_fits_file = Path(r"D:\data\astro\ratan-600\fast_acquisition\1-3ghz\fits\2024\08\2024-08-01_121957_sun+00.fits")
    # writer.save(output_fits_file)

def _get_output_fits_filename(observation: FastAcquisition1To3GHzObservation, fits_output_path : Path) -> Path:
    culm_efr = observation.metadata.datetime_culmination_efrat_utc
    year = culm_efr.year
    month_str = f"{culm_efr.month:02d}"
    obs_file = observation.metadata.obs_file
    base_filename = obs_file.name.split('.', 1)[0]
    output_fits_file = Path(fits_output_path / f"{year}" / month_str / f"{base_filename}.fits")
    return output_fits_file

def _print_header_params(observation: FastAcquisition1To3GHzObservation):
    metadata = observation.metadata
    print(f"Time start: {metadata.datetime_reg_start_utc}")
    print(f"Culmination Efrat: {metadata.datetime_culmination_efrat_utc}")
    print(f"Culmination horn: {metadata.datetime_culmination_feed_horn_utc}")
    print(f"Time stop: {metadata.datetime_reg_stop_utc}")
    print(f"Record duration, sec: {metadata.record_duration_seconds}")
    print(f"Time reduction factor: {metadata.time_reduction_factor}")
    print(f"Number of samples: {metadata.num_samples}")
    print(f"Samples per second: {metadata.samples_per_second}")
    print(f"Arcsec per second: {metadata.arcsec_per_second}")
    print(f"Arcsec per sample: {metadata.arcsec_per_sample}")
    print(f"Ref time: {metadata.ref_time}")
    print(
        f"До кульминации: {(metadata.datetime_culmination_feed_horn_utc - metadata.datetime_reg_start_utc).total_seconds()}")
    print(
        f"После кульминации: {(metadata.datetime_reg_stop_utc - metadata.datetime_culmination_feed_horn_utc).total_seconds()}")
    print(f"Ref sample {metadata.ref_sample}")
    print(f"arcsec L {- metadata.ref_sample * metadata.arcsec_per_sample}")
    print(
        f"arcsec last sample {metadata.num_samples * metadata.arcsec_per_sample - metadata.ref_sample * metadata.arcsec_per_sample}")
    print(f"time resolution: {metadata.time_resolution}")
    print(f"switch polarization time: {metadata.switch_polarization_time}")

    # print(f"До 1го импульса: {metadata.start_pulse_edge_time - metadata.datetime_reg_start_utc}")
    # print(f"От 1го импульса: {metadata.datetime_culmination_feed_horn_utc - metadata.start_pulse_edge_time}")
    # print(f"До 2го импульса: {metadata.stop_pulse_edge_time - metadata.datetime_culmination_feed_horn_utc}")
    # print(f"После 2го импульса: {metadata.datetime_reg_stop_utc - metadata.stop_pulse_edge_time}")

@time_counter
def read_fits(fits_file: Path):

    try:
        with fits.open(fits_file) as hdul:
            print(hdul.info())
            primary_hdu = hdul[0]
            compressed_image_hdu = hdul[1]
            table_hdu = hdul[2]

            header = copy.deepcopy(primary_hdu.header)
            data_array = copy.deepcopy(compressed_image_hdu.data)
            table_data = copy.deepcopy(table_hdu.data)
    except FileNotFoundError:
        print(f"Fits file ''{fits_file}'' not found")
    except Exception as e:
        print(f"Error {e}")

    for card in header.cards:
        print(f"{card.keyword}  {card.value} // {card.comment}")

    column_names = table_data.columns.names
    print(column_names)
    frequencies = table_data['freq']
    # print(f"Frequencies: {frequencies}")
    if 'cal_p0' in table_hdu.columns.names:
        calibr_coeff_p0 = table_data['cal_p0']
        calibr_coeff_p1 = table_data['cal_p1']
        print(f"Calibration coefficients: {calibr_coeff_p0}")

    num_frequencies = header['NFREQS']
    num_samples = header['NSAMPLES']
    ref_time = header['REF_TIME']
    arcsec_per_second = header['ARCPSEC']
    az = header['AZIMUTH']
    az = f'{round(az):+d}'

    datetime_obs = header['CULM_FEE']
    datetime_obs = datetime.strptime(datetime_obs, '%Y-%m-%dT%H:%M:%S.%f%z')
    datatime_str = datetime_obs.strftime('%Y-%m-%d %H:%M:%S %Z')
    frequency_axis = np.linspace(config.freq_min, config.freq_max, num=num_frequencies, dtype=np.float64)

    time_axis = np.arange(num_samples) / config.samples_per_second
    arcsec_axis = - (time_axis - ref_time) * arcsec_per_second

    pol = 0

    data = data_array[:,pol,:]

    matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
    fig, ax = plt.subplots()
    # im = ax.pcolormesh(full_arcsec_scale, freq_selection, pol0_data_selection_calibrated,
    #                    shading='gouraud', cmap='Spectral_r')
    contour = ax.contourf(arcsec_axis, frequency_axis, data, levels=100,
                          cmap='Spectral_r')
    ax.set_xlabel('x, arcsec')
    ax.set_ylabel('Frequency, MHz')
    ax.set_title(f"{datatime_str} Az {az}\nSpectrogram LHCP")
    fig.colorbar(contour, ax=ax, label='s.f.u.')
    #plt.show()

    polarization = 0
    #data_array[data_array == 2] = np.nan
    #data_array[data_array == 1] = np.nan

    matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
    plt.figure(figsize=(12, 7))
    for freq_idx in range(data_array.shape[0]):
        plt.plot(arcsec_axis, data_array[freq_idx, polarization, :],
                alpha=0.5,
                linewidth = 1,
                marker = 'o',
                markersize = 2
        )
    plt.grid(alpha=0.3)
    plt.xlabel('x, arcsec')
    plt.ylabel('flux, s.f.u.')
    plt.title(f"{datatime_str} Az {az}\nLHCP")
    plt.tight_layout()
    plt.show()
    return data_array

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
    process_observations()

if __name__ == "__main__":
  main()
