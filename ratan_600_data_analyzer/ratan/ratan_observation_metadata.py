from abc import abstractmethod, ABC
from datetime import datetime

from ratan_600_data_analyzer.observation.observation_metadata import ObservationMetadata
from ratan_600_data_analyzer.ratan.data_layout import DataLayout


class RatanObservationMetadata(ObservationMetadata, ABC):

    """
    Поля
    data_receiver // приемный комплекс
    polarization_components // "LR" "IV"

    telescope
    object
    azimuth
    altitude //
    declination // dec
    right_ascension // sol_ra, ra

    solar_radius // solar_r
    solar_position_angle // solar_p
    solar_b_angle // solar_b

    startobs_utc
    startobs_local
    stopobs_utc
    stopobs_local
    datetime_culmination_utc
    datetime_culmination_local

    cdelt1

    data_layout

    is_bad
    is_calibrated

    """

    @property
    @abstractmethod
    def obs_file(self):
        pass

    @obs_file.setter
    @abstractmethod
    def obs_file(self, obs_file):
        pass

    @property
    @abstractmethod
    def data_receiver(self):
        pass

    @data_receiver.setter
    @abstractmethod
    def data_receiver(self, data_receiver):
        pass

    @property
    @abstractmethod
    def polarization_components(self):
        pass

    @polarization_components.setter
    @abstractmethod
    def polarization_components(self, value):
        pass

    @property
    @abstractmethod
    def telescope(self) -> str:
        pass

    @telescope.setter
    @abstractmethod
    def telescope(self, value: str):
        pass

    @property
    @abstractmethod
    def observation_object(self) -> str:
        pass

    @observation_object.setter
    @abstractmethod
    def observation_object(self, value: str):
        pass

    @property
    @abstractmethod
    def azimuth(self) -> float:
        pass

    @azimuth.setter
    @abstractmethod
    def azimuth(self, value: float):
        pass

    @property
    @abstractmethod
    def altitude(self) -> float:
        pass

    @altitude.setter
    @abstractmethod
    def altitude(self, value: float):
        pass

    @property
    @abstractmethod
    def declination(self) -> float:
        pass

    @declination.setter
    @abstractmethod
    def declination(self, value: float):
        pass

    @property
    @abstractmethod
    def right_ascension(self) -> float:
        pass

    @right_ascension.setter
    @abstractmethod
    def right_ascension(self, value: float):
        pass

    @property
    @abstractmethod
    def solar_radius(self) -> float:
        pass

    @solar_radius.setter
    @abstractmethod
    def solar_radius(self, value: float):
        pass

    @property
    @abstractmethod
    def solar_position_angle(self) -> float:
        pass

    @solar_position_angle.setter
    @abstractmethod
    def solar_position_angle(self, value: float):
        pass

    @property
    @abstractmethod
    def solar_b_angle(self) -> float:
        pass

    @solar_b_angle.setter
    @abstractmethod
    def solar_b_angle(self, value: float):
        pass

    @property
    @abstractmethod
    def datetime_reg_start_utc(self) -> datetime:
        pass

    @datetime_reg_start_utc.setter
    @abstractmethod
    def datetime_reg_start_utc(self, value: datetime):
        pass

    @property
    @abstractmethod
    def datetime_reg_start_local(self) -> datetime:
        pass

    @datetime_reg_start_local.setter
    @abstractmethod
    def datetime_reg_start_local(self, value: datetime):
        pass

    @property
    @abstractmethod
    def datetime_reg_stop_utc(self) -> datetime:
        pass

    @datetime_reg_stop_utc.setter
    @abstractmethod
    def datetime_reg_stop_utc(self, value: datetime):
        pass

    @property
    @abstractmethod
    def datetime_culmination_utc(self) -> datetime:
        pass

    @datetime_culmination_utc.setter
    @abstractmethod
    def datetime_culmination_utc(self, value: datetime):
        pass

    @property
    @abstractmethod
    def datetime_culmination_local(self) -> datetime:
        pass

    @datetime_culmination_local.setter
    @abstractmethod
    def datetime_culmination_local(self, value: datetime):
        pass

    @property
    @abstractmethod
    def cdelt1(self) -> float:
        pass

    @cdelt1.setter
    @abstractmethod
    def cdelt1(self, value: float):
        pass

    @property
    @abstractmethod
    def data_layout(self) -> DataLayout:
        pass

    @data_layout.setter
    @abstractmethod
    def data_layout(self, value: DataLayout):
        pass

    @property
    @abstractmethod
    def is_bad(self) -> bool:
        pass

    @is_bad.setter
    @abstractmethod
    def is_bad(self, value: bool):
        pass

    @property
    @abstractmethod
    def is_calibrated(self) -> bool:
        pass

    @is_calibrated.setter
    @abstractmethod
    def is_calibrated(self, value: bool):
        pass

    @property
    @abstractmethod
    def data_file_extension(self):
        pass

    @data_file_extension.setter
    @abstractmethod
    def data_file_extension(self, data_file_extension):
        pass