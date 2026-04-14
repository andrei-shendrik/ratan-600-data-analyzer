from enum import Enum


class PolarizationType(Enum):

    """
    polarization = PolarizationType.LHCP

    """

    LHCP = "LHCP"
    RHCP = "RHCP"
    STOKES_I = "Stokes I"
    STOKES_V = "Stokes V"