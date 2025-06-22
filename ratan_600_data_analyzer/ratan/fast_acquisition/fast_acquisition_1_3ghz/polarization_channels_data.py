from dataclasses import dataclass

import numpy as np


@dataclass
class PolarizationChannelsData:

    """
            c0 1-2 GHz
            c1 2-3 GHz
    """
    _c0p0_data: np.ndarray
    _c0p1_data: np.ndarray
    _c1p0_data: np.ndarray
    _c1p1_data: np.ndarray