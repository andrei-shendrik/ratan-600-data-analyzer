import copy

from ratan_600_data_analyzer.ratan.ratan_observation_metadata import RatanObservationMetadata


class FastAcquisition1To3GHzMetadata(RatanObservationMetadata):

    """
        Внимание,
        frequencies, polarizations никак не привязаны к массиву, порядок элементов значения не имеет,
        они определяют список доступных частот и поляризаций в данных.

        Порядок доступа к элементам массива задают:
        data_layout.frequency_axis
        data_layout.polarization_axis

        FastAcquisition (1-3GHz) metadata

        attenuator_common
        attenuator_1_2ghz
        attenuator_2_3ghz

        average_points
        kurtosis_lower_bound_1_2ghz
        kurtosis_upper_bound_1_2ghz
        kurtosis_lower_bound_2_3ghz
        kurtosis_upper_bound_2_3ghz

        desc file

        Object: sun
        Azimuth: 0
        Culmination: 2024-06-05T12:12:12.890000+03:00
        Feed offset: 43
        Feed offset time: 44.208052
        Result: SUCCESS

        {
            "feed_offset": 43,
            "record_duration_rlc": [-205, 205],
            "pulse1_rlc": [-200, -195],
            "pulse2_rlc": [195, 200],
            "acquisition_parameters": {
                "average_points": 32,
                "kurtosis_lower_bound_12ghz": -20,
                "kurtosis_upper_bound_12ghz": 20,
                "kurtosis_lower_bound_23ghz": -20,
                "kurtosis_upper_bound_23ghz": 20,
                "attenuator_12ghz": 0,
                "attenuator_23ghz": 0,
                "attenuator_common": -20,
                "polarization": 0,
                "noise_generator": 0,
                "auto_polarization_switch": 1
            },
            "override_mainobs": False,
            "azimuth": 0,
            "object": "sun",
            "culmination": "2024-06-05T12:12:12.890000+03:00",
            "feed_offset_time": 44.208052,
            "fits_words": {
                "OBJECT": "sun",
                "T_OBS": "2024-06-05T12:12:12.890000+03:00",
                "AZIMUTH": "+0",
                "ALTITUDE": "68.742417",
                "DEC": "22.616",
                "RA": "04.929",
                "SOLAR_R": "945.800",
                "SOLAR_P": "-13.700",
                "SOLAR_B": "-0.100",
                "FEED_OFFSET_TIME": "44.208052"
            },
            "start_time": "2024-06-05T12:08:32.098052+03:00"
        }
    """

    def __init__(self):
        super().__init__()
        self._obs_file = None
        self._bin_file = None
        self._desc_file = None
        self._data_receiver = None
        self._data_file_extension = None

        self._is_bad = None
        # "LHCP / RHCP"
        # "Stokes I / Stokes V"

        # Flag_IV 0 1
        # "LR / IV"

        # channel mapping
        # POL_CH0 = "LHCP"
        # POL_CH1 = "RHCP"

        self._datetime_reg_start_utc = None # startobs
        self._datetime_reg_start_local = None

        self._datetime_culmination_efrat_local = None
        self._datetime_culmination_efrat_utc = None

        self._datetime_culmination_feed_horn_local = None
        self._datetime_culmination_feed_horn_utc = None

        self._datetime_reg_stop_utc = None # stopobs
        self._datetime_reg_stop_local = None

        self._record_duration_seconds = None

        self._channel_mapping = None

        self._frequencies = None  # массив частот
        self._polarizations = None

        self._telescope = None
        self._observation_object = None
        self._azimuth = None
        self._altitude = None
        self._declination = None
        self._right_ascension = None

        self._solar_radius = None
        self._solar_position_angle = None # solar_q
        self._solar_b_angle = None

        self._coordinate_axes = None
        self._num_samples = None  # количество временных отсчетов
        self._num_frequencies = None  # spectrum_length
        self._ref_time = None
        self._ref_sample = None

        self._samples_per_second = None
        self._arcsec_per_sample = None
        self._arcsec_per_second = None

        self._time_reduction_factor = None
        self._frequency_resolution = None # MHz
        self._time_resolution = None # sec
        self._arcsec_resolution = None
        self._switch_polarization_time = None # sec

        self._start_pulse_edge_sample = None
        self._stop_pulse_edge_sample = None
        self._start_pulse_edge_time = None
        self._stop_pulse_edge_time = None

        self._feed_offset = None
        self._feed_offset_time = None

        self._attenuator_common = None
        self._attenuator_1_2ghz = None
        self._attenuator_2_3ghz = None

        self._average_points = None
        self._half_width_kurtosis_interval = None
        # self._kurtosis_lower_bound_1_2ghz = None
        # self._kurtosis_upper_bound_1_2ghz = None
        # self._kurtosis_lower_bound_2_3ghz = None
        # self._kurtosis_upper_bound_2_3ghz = None

        self._auto_polarization_switch = None
        self._feed_horn_offset = None
        self._feed_horn_offset_time = None
        self._noise_generator = None
        self._polarization_components = None
        self._pulse1_rlc = None
        self._pulse2_rlc = None
        self._record_duration_rlc = None

        self._is_calibrated = None
        self._calibration_coefficients = None
        self._unit = None
        self._quiet_sun_point_arcsec = None

    @property
    def obs_file(self):
        return self._bin_file

    @obs_file.setter
    def obs_file(self, obs_file):
        self._bin_file = obs_file

    @property
    def bin_file(self):
        return self._bin_file

    @bin_file.setter
    def bin_file(self, value):
        self._bin_file = value

    @property
    def desc_file(self):
        return self._desc_file

    @desc_file.setter
    def desc_file(self, value):
        self._desc_file = value

    @property
    def datetime_reg_start_utc(self):
        return self._datetime_reg_start_utc

    @datetime_reg_start_utc.setter
    def datetime_reg_start_utc(self, value):
        self._datetime_reg_start_utc = value

    @property
    def datetime_reg_start_local(self):
        return self._datetime_reg_start_local

    @datetime_reg_start_local.setter
    def datetime_reg_start_local(self, value):
        self._datetime_reg_start_local = value

    @property
    def datetime_culmination_efrat_local(self):
        return self._datetime_culmination_efrat_local

    @datetime_culmination_efrat_local.setter
    def datetime_culmination_efrat_local(self, value):
        self._datetime_culmination_efrat_local = value

    @property
    def datetime_culmination_efrat_utc(self):
        return self._datetime_culmination_efrat_utc

    @datetime_culmination_efrat_utc.setter
    def datetime_culmination_efrat_utc(self, value):
        self._datetime_culmination_efrat_utc = value

    @property
    def datetime_culmination_feed_horn_local(self):
        return self._datetime_culmination_feed_horn_local

    @datetime_culmination_feed_horn_local.setter
    def datetime_culmination_feed_horn_local(self, value):
        self._datetime_culmination_feed_horn_local = value

    @property
    def datetime_culmination_feed_horn_utc(self):
        return self._datetime_culmination_feed_horn_utc

    @datetime_culmination_feed_horn_utc.setter
    def datetime_culmination_feed_horn_utc(self, value):
        self._datetime_culmination_feed_horn_utc = value

    @property
    def datetime_reg_stop_utc(self):
        return self._datetime_reg_stop_utc

    @datetime_reg_stop_utc.setter
    def datetime_reg_stop_utc(self, value):
        self._datetime_reg_stop_utc = value

    @property
    def datetime_reg_stop_local(self):
        return self._datetime_reg_stop_local

    @datetime_reg_stop_local.setter
    def datetime_reg_stop_local(self, value):
        self._datetime_reg_stop_local = value

    @property
    def frequencies(self):
        return self._frequencies

    @frequencies.setter
    def frequencies(self, value):
        self._frequencies = value

    @property
    def polarizations(self):
        return self._polarizations

    @polarizations.setter
    def polarizations(self, value):
        self._polarizations = value

    @property
    def num_samples(self):
        return self._num_samples

    @num_samples.setter
    def num_samples(self, value):
        self._num_samples = value

    @property
    def flag_iv(self):
        return self._flag_iv

    @flag_iv.setter
    def flag_iv(self, value):
        self._flag_iv = value

    @property
    def time_reduction_factor(self):
        return self._time_reduction_factor

    @time_reduction_factor.setter
    def time_reduction_factor(self, value):
        self._time_reduction_factor = value

    @property
    def telescope(self):
        return self._telescope

    @telescope.setter
    def telescope(self, value):
        self._telescope = value

    @property
    def observation_object(self):
        return self._observation_object

    @observation_object.setter
    def observation_object(self, value):
        self._observation_object = value

    @property
    def azimuth(self):
        return self._azimuth

    @azimuth.setter
    def azimuth(self, value):
        self._azimuth = value

    @property
    def solar_p(self):
        return self._solar_p

    @solar_p.setter
    def solar_p(self, value):
        self._solar_p = value

    @property
    def solar_b(self):
        return self._solar_b

    @solar_b.setter
    def solar_b(self, value):
        self._solar_b = value

    @property
    def solar_r(self):
        return self._solar_r

    @solar_r.setter
    def solar_r(self, value):
        self._solar_r = value

    @property
    def altitude(self):
        return self._altitude

    @altitude.setter
    def altitude(self, value):
        self._altitude = value

    @property
    def right_ascension(self):
        return self._right_ascension

    @right_ascension.setter
    def right_ascension(self, value):
        self._right_ascension = value

    @property
    def declination(self):
        return self._declination

    @declination.setter
    def declination(self, value):
        self._declination = value

    @property
    def data_receiver(self):
        return self._data_receiver

    @data_receiver.setter
    def data_receiver(self, value):
        self._data_receiver = value

    @property
    def data_file_extension(self):
        return self._data_file_extension

    @data_file_extension.setter
    def data_file_extension(self, value):
        self._data_file_extension = value

    @property
    def cdelt1(self):
        return self._cdelt1

    @cdelt1.setter
    def cdelt1(self, value):
        self._cdelt1 = value

    @property
    def auto_polarization_switch(self):
        return self._auto_polarization_switch

    @auto_polarization_switch.setter
    def auto_polarization_switch(self, value):
        self._auto_polarization_switch = value

    @property
    def feedhorn_offset(self):
        return self._feedhorn_offset

    @feedhorn_offset.setter
    def feedhorn_offset(self, value):
        self._feedhorn_offset = value

    @property
    def feedhorn_offset_time(self):
        return self._feedhorn_offset_time

    @feedhorn_offset_time.setter
    def feedhorn_offset_time(self, value):
        self._feedhorn_offset_time = value

    @property
    def is_bad(self):
        return self._is_bad

    @is_bad.setter
    def is_bad(self, value):
        self._is_bad = value

    @property
    def is_calibrated(self):
        return self._is_calibrated

    @is_calibrated.setter
    def is_calibrated(self, value):
        self._is_calibrated = value

    @property
    def noise_generator(self):
        return self._noise_generator

    @noise_generator.setter
    def noise_generator(self, value):
        self._noise_generator = value

    @property
    def polarization_components(self):
        return self._polarization_components

    @polarization_components.setter
    def polarization_components(self, value):
        self._polarization_components = value

    @property
    def pulse1_rlc(self):
        return self._pulse1_rlc

    @pulse1_rlc.setter
    def pulse1_rlc(self, value):
        self._pulse1_rlc = value

    @property
    def pulse2_rlc(self):
        return self._pulse2_rlc

    @pulse2_rlc.setter
    def pulse2_rlc(self, value):
        self._pulse2_rlc = value

    @property
    def record_duration_rlc(self):
        return self._record_duration_rlc

    @record_duration_rlc.setter
    def record_duration_rlc(self, value):
        self._record_duration_rlc = value

    @property
    def solar_b_angle(self):
        return self._solar_b_angle

    @solar_b_angle.setter
    def solar_b_angle(self, value):
        self._solar_b_angle = value

    @property
    def solar_position_angle(self):
        return self._solar_position_angle

    @solar_position_angle.setter
    def solar_position_angle(self, value):
        self._solar_position_angle = value

    @property
    def solar_radius(self):
        return self._solar_radius

    @solar_radius.setter
    def solar_radius(self, value):
        self._solar_radius = value

    @property
    def start_pulse_edge_sample(self):
        return self._start_pulse_edge_sample

    @start_pulse_edge_sample.setter
    def start_pulse_edge_sample(self, value):
        self._start_pulse_edge_sample = value

    @property
    def stop_pulse_edge_sample(self):
        return self._stop_pulse_edge_sample

    @stop_pulse_edge_sample.setter
    def stop_pulse_edge_sample(self, value):
        self._stop_pulse_edge_sample = value

    @property
    def arcsec_per_second(self):
        return self._arcsec_per_second

    @arcsec_per_second.setter
    def arcsec_per_second(self, value):
        self._arcsec_per_second = value

    @property
    def arcsec_per_sample(self):
        return self._arcsec_per_sample

    @arcsec_per_sample.setter
    def arcsec_per_sample(self, value):
        self._arcsec_per_sample = value

    @property
    def ref_sample(self):
        return self._ref_sample

    @ref_sample.setter
    def ref_sample(self, value):
        self._ref_sample = value

    @property
    def ref_time(self):
        return self._ref_time

    @ref_time.setter
    def ref_time(self, value):
        self._ref_time = value

    @property
    def feed_offset(self):
        return self._feed_offset

    @feed_offset.setter
    def feed_offset(self, value):
        self._feed_offset = value

    @property
    def feed_offset_time(self):
        return self._feed_offset_time

    @feed_offset_time.setter
    def feed_offset_time(self, value):
        self._feed_offset_time = value

    @property
    def attenuator_common(self):
        return self._attenuator_common

    @attenuator_common.setter
    def attenuator_common(self, value):
        self._attenuator_common = value

    @property
    def attenuator_1_2ghz(self):
        return self._attenuator_1_2ghz

    @attenuator_1_2ghz.setter
    def attenuator_1_2ghz(self, value):
        self._attenuator_1_2ghz = value

    @property
    def attenuator_2_3ghz(self):
        return self._attenuator_2_3ghz

    @attenuator_2_3ghz.setter
    def attenuator_2_3ghz(self, value):
        self._attenuator_2_3ghz = value

    @property
    def samples_per_second(self):
        return self._samples_per_second

    @samples_per_second.setter
    def samples_per_second(self, value):
        self._samples_per_second = value

    @property
    def start_pulse_edge_time(self):
        return self._start_pulse_edge_time

    @start_pulse_edge_time.setter
    def start_pulse_edge_time(self, value):
        self._start_pulse_edge_time = value

    @property
    def stop_pulse_edge_time(self):
        return self._stop_pulse_edge_time

    @stop_pulse_edge_time.setter
    def stop_pulse_edge_time(self, value):
        self._stop_pulse_edge_time = value

    @property
    def record_duration_seconds(self):
        return self._record_duration_seconds

    @record_duration_seconds.setter
    def record_duration_seconds(self, value):
        self._record_duration_seconds = value

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, value):
        self._unit = value

    @property
    def coordinate_axes(self):
        return self._coordinate_axes

    @coordinate_axes.setter
    def coordinate_axes(self, value):
        self._coordinate_axes = value

    @property
    def num_frequencies(self):
        return self._num_frequencies

    @num_frequencies.setter
    def num_frequencies(self, value):
        self._num_frequencies = value

    @property
    def frequency_resolution(self):
        return self._frequency_resolution

    @frequency_resolution.setter
    def frequency_resolution(self, value):
        self._frequency_resolution = value

    @property
    def time_resolution(self):
        return self._time_resolution

    @time_resolution.setter
    def time_resolution(self, value):
        self._time_resolution = value

    @property
    def arcsec_resolution(self):
        return self._arcsec_resolution

    @arcsec_resolution.setter
    def arcsec_resolution(self, value):
        self._arcsec_resolution = value

    @property
    def switch_polarization_time(self):
        return self._switch_polarization_time

    @switch_polarization_time.setter
    def switch_polarization_time(self, value):
        self._switch_polarization_time = value

    @property
    def calibration_coefficients(self):
        return self._calibration_coefficients

    @calibration_coefficients.setter
    def calibration_coefficients(self, array):
        self._calibration_coefficients = copy.deepcopy(array)

    @property
    def half_width_kurtosis_interval(self):
        return self._half_width_kurtosis_interval

    @half_width_kurtosis_interval.setter
    def half_width_kurtosis_interval(self, value):
        self._half_width_kurtosis_interval = value