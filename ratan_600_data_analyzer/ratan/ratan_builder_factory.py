from pathlib import Path
from typing import TypeGuard, Union

from ratan_600_data_analyzer.ratan.data_receiver import DataReceiver
from ratan_600_data_analyzer.ratan.fast_acquisition.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_builder import \
    FastAcquisition1To3GHzBuilder
from ratan_600_data_analyzer.ratan.ratan_observation_builder import RatanObservationBuilder
from ratan_600_data_analyzer.ratan.sspc.sspc_builder import SSPCBuilder


class RatanBuilderFactory:

    @staticmethod
    def create_builder(file: Path) -> Union[FastAcquisition1To3GHzBuilder, SSPCBuilder]:
        # todo
        # временно, переделать
        if file.suffix.lower() == '.bin':
            builder = FastAcquisition1To3GHzBuilder(file)
            builder.receiver = DataReceiver.FAST_ACQUISITION_1_3GHZ
            return builder
        if file.suffix.lower() == '.fits':
            builder = SSPCBuilder(file)
            builder.receiver = DataReceiver.SSPC
            return builder
        raise ValueError(f"No suitable builders found for file: {file}")

    @staticmethod
    def is_fast_1_3ghz_builder(builder: RatanObservationBuilder) -> TypeGuard[FastAcquisition1To3GHzBuilder]:
        return builder.receiver == DataReceiver.FAST_ACQUISITION_1_3GHZ

    @staticmethod
    def is_sspc_builder(builder: RatanObservationBuilder) -> TypeGuard[SSPCBuilder]:
        result = ((builder.receiver == DataReceiver.SSPC_16) or
                  (builder.receiver == DataReceiver.SSPC))
        return result