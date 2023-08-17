"""Implementation of receive card."""
from dataclasses import dataclass

from console.spcm_control.device_interface import SpectrumDevice
from console.spcm_control.spcm.pyspcm import *  # noqa # pylint: disable=unused-wildcard-import
from console.spcm_control.spcm.spcm_tools import *  # noqa # pylint: disable=unused-wildcard-import


@dataclass
class RxCard(SpectrumDevice):
    """Implementation of TX device."""

    path: str

    __name__: str = "RxCard"

    def __post_init__(self):
        super().__init__(self.path)

    def setup_card(self):
        pass

    def start_operation(self):
        pass
    
    def stop_operation(self):
        pass

    def get_status(self):
        pass
