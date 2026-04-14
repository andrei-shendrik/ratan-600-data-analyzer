from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation
from ratan_600_data_analyzer.ratan.ratan_observation_data import RatanObservationData
from ratan_600_data_analyzer.ratan.sspc.sspc_data import SSPCData


class SSPCObservation(RatanObservation):
    def __init__(self, metadata, data: RatanObservationData):
        super().__init__(metadata, data)

    @property
    def metadata(self):
        return self._metadata

    @property
    def data(self) -> SSPCData:
        return self._data