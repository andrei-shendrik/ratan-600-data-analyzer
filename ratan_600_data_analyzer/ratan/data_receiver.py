from enum import Enum


class DataReceiver(Enum):
    """
        Приемные комплексы

        SSPC = Solar spectral polarization complex (Солнечный спектрально-поляризационный комплекс, до 2016г.)
        SSPC_16 = Solar spectral polarization complex SSPC-16 (Солнечный спектрально-поляризационный комплекс ССПК-16, с 2016г.)

    """

    FAST_ACQUISITION_1_3GHZ = "Fast Acquisition 1-3 GHz"
    FAST_ACQUISITION_3_18GHZ = "Fast Acquisition 3-18 GHz"
    SSPC = "Solar spectral polarization complex"
    SSPC_16 = "Solar spectral polarization complex SSPC-16"

    @property
    def is_sspc(self) -> bool:
        return self in {DataReceiver.SSPC, DataReceiver.SSPC_16}