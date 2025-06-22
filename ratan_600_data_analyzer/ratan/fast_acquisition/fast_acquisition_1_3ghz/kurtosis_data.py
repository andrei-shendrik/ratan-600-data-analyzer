from dataclasses import dataclass

import numpy as np


@dataclass
class KurtosisData:
    """
            c0 1-2 GHz
            c1 2-3 GHz
    """
    _c0p0_kurt: np.ndarray
    _c0p1_kurt: np.ndarray
    _c1p0_kurt: np.ndarray
    _c1p1_kurt: np.ndarray