"""Global acquisition parameter."""
import os

from console.interfaces.interface_acquisition_parameter import AcquisitionParameter

# Load state of acquisition parameters from file, if it exists
parameter = AcquisitionParameter().load() if os.path.exists("acq-param-state.pkl") else AcquisitionParameter()


def update(**change) -> None:
    """Update global acquisition parameter variable."""
    global parameter
    parameter = parameter.update(**change)
