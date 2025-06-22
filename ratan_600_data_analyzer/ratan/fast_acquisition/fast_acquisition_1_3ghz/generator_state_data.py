from dataclasses import dataclass

import numpy as np


@dataclass
class GeneratorStateData:
    """
            c0 1-2 GHz
            c1 2-3 GHz
    """
    _c0p0_state: np.ndarray
    _c0p1_state: np.ndarray
    _c1p0_state: np.ndarray
    _c1p1_state: np.ndarray