from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_constants import TIME_REDUCTION_FACTOR, FREQ_MIN, FREQ_MAX
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
        self._bin_file = None
        self._desc_file = None
        self._data_receiver = None
        self._data_file_extension = None

        self._datetime_reg_start_utc = None
        self._datetime_reg_start_local = None

        self._datetime_culmination_utc = None
        self._datetime_culmination_local = None

        self._datetime_reg_stop_utc = None
        self._datetime_reg_stop_local = None

        self._frequencies = None  # массив частот
        self._polarizations = None

        self._samples = None  # количество временных отсчетов
        self._time_reduction_factor = TIME_REDUCTION_FACTOR

        self._telescope = None
        self._observation_object = None
        self._azimuth = None
        self._altitude = None
        self._declination = None
        self._right_ascension = None

        self._solar_radius = None
        self._solar_position_angle = None
        self._solar_b_angle = None

        self._startobs_utc = None
        self._startobs_local = None
        self._stopobs_utc = None
        self._stopobs_local = None
        self._datetime_culmination_utc = None
        self._datetime_culmination_local = None

        self._cdelt1 = None
        self._data_layout = None

        self._is_bad = None
        self._is_calibrated = None

        self._attenuator_common = None
        self._attenuator_1_2ghz = None
        self._attenuator_2_3ghz = None

        self._average_points = None
        self._kurtosis_lower_bound_1_2ghz = None
        self._kurtosis_upper_bound_1_2ghz = None
        self._kurtosis_lower_bound_2_3ghz = None
        self._kurtosis_upper_bound_2_3ghz = None

        self._observation_object = None
        self._cdelt1 = None
        self._auto_polarization_switch = None
        self._datetime_culmination_efrat_local = None
        self._datetime_culmination_efrat_utc = None
        self._datetime_culmination_feedhorn_local = None
        self._datetime_culmination_feedhorn_utc = None
        self._declination = None
        self._feedhorn_offset = None
        self._feedhorn_offset_time = None
        self._is_bad = None
        self._is_calibrated = None
        self._noise_generator = None
        self._polarization_components = None
        self._pulse1_rlc = None
        self._pulse2_rlc = None
        self._record_duration_rlc = None
        self._right_ascension = None
        self._solar_b_angle = None
        self._solar_position_angle = None
        self._solar_radius = None
        self._startobs_local = None
        self._startobs_utc = None
        self._stopobs_local = None
        self._stopobs_utc = None

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
    def datetime_culmination_utc(self):
        return self._datetime_culmination_utc

    @datetime_culmination_utc.setter
    def datetime_culmination_utc(self, value):
        self._datetime_culmination_utc = value

    @property
    def datetime_culmination_local(self):
        return self._datetime_culmination_local

    @datetime_culmination_local.setter
    def datetime_culmination_local(self, value):
        self._datetime_culmination_local = value

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
    def samples(self):
        return self._samples

    @samples.setter
    def samples(self, value):
        self._samples = value

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
    def solar_declination(self):
        return self._solar_declination

    @solar_declination.setter
    def solar_declination(self, value):
        self._solar_declination = value

    @property
    def solar_ra(self):
        return self._solar_ra

    @solar_ra.setter
    def solar_ra(self, value):
        self._solar_ra = value

    @property
    def data_layout(self):
        return self._data_layout

    @data_layout.setter
    def data_layout(self, value):
        self._data_layout = value

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
    def datetime_culmination_feedhorn_local(self):
        return self._datetime_culmination_feedhorn_local

    @datetime_culmination_feedhorn_local.setter
    def datetime_culmination_feedhorn_local(self, value):
        self._datetime_culmination_feedhorn_local = value

    @property
    def datetime_culmination_feedhorn_utc(self):
        return self._datetime_culmination_feedhorn_utc

    @datetime_culmination_feedhorn_utc.setter
    def datetime_culmination_feedhorn_utc(self, value):
        self._datetime_culmination_feedhorn_utc = value

    @property
    def declination(self):
        return self._declination

    @declination.setter
    def declination(self, value):
        self._declination = value

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
    def right_ascension(self):
        return self._right_ascension

    @right_ascension.setter
    def right_ascension(self, value):
        self._right_ascension = value

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