"""Implementation of synchronization card namely star-hub."""
import ctypes
import logging
import threading
from dataclasses import dataclass

import numpy as np
import sys
import console.spcm_control.spcm.pyspcm as spcm
from console.interfaces.interface_acquisition_parameter import Dimensions
from console.interfaces.interface_unrolled_sequence import UnrolledSequence
from console.spcm_control.abstract_device import SpectrumDevice
from console.spcm_control.spcm.tools import create_dma_buffer, translate_status, type_to_name
from console.spcm_control.spcm.errors import *


@dataclass
class SyncCard(SpectrumDevice):

    path: str
    
    __name__: str = "SyncCard"
    
    def __post_init__(self):
        """Post init function which is required to use dataclass arguments."""
        self.log = logging.getLogger(self.__name__)
        super().__init__(self.path, log=self.log)
        
        self.card_type = spcm.int32(0)
    
        # Threading class attributes
        self.worker: threading.Thread | None = None
        self.is_running = threading.Event()
    def dict(self) -> dict:
        """Returnt class variables which are json serializable as dictionary.

        Returns
        -------
            Dictionary containing class variables.
        """
        return super().dict()
        
    def setup_card(self) -> None:
        """Set up spectrum card transmit (TX) cards in synchronization mode.

        At the very beginning, a card reset is performed. The clock mode is set according to the sample rate,
        defined by the class attribute.

        Raises
        ------
        To be implemented
        """
        spcm_dwSetParam_i32 (self.card,  SPC_SYNC_ENABLEMASK, 0x0003)
        self.log.debug("Sync device setup completed")
        self.log_card_status()
        
    def start_operation(self) -> None:
        error = spcm.spcm_dwSetParam_i32(
                self.card,
                spcm.SPC_M2CMD,
                spcm.M2CMD_CARD_START | spcm.M2CMD_CARD_ENABLETRIGGER,
            )
        self.handle_error(error)
    def stop_operation(self) -> None:
        """Stop card operation by thread event and stop card."""
        if self.worker is not None:
            self.is_running.set()
            self.worker.join()

            error = spcm.spcm_dwSetParam_i32(
                self.card,
                spcm.SPC_M2CMD,
                spcm.M2CMD_CARD_STOP | spcm.M2CMD_DATA_STOPDMA,
            )

            self.handle_error(error)
            self.worker = None
        else:
            print("No active replay thread found...")
    
    def get_status(self) -> int:
        """Get the current card status.

        Returns
        -------
            String with status description.
        """
        try:
            if not self.card:
                raise ConnectionError("No device found")
        except ConnectionError as err:
            self.log.exception(err, exc_info=True)
            raise err
        status = spcm.int32(0)
        spcm.spcm_dwGetParam_i32(self.card, spcm.SPC_M2STATUS, ctypes.byref(status))
        return status.value
        
    def log_card_status(self, include_desc: bool = False) -> None:
        """Log current card status.

        The status is represented by a list. Each entry represents a possible card status in form
        of a (sub-)list. It contains the status code, name and (optional) description of the spectrum
        instrumentation manual.

        Parameters
        ----------
        include_desc, optional
            Flag which indicates if description string should be contained in status entry, by default False
        """
        msg, _ = translate_status(self.get_status(), include_desc=include_desc)
        status = {key: val for val, key in msg.values()}
        self.log.debug("Card status:\n%s", status)