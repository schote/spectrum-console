"""Constructor for spin-echo spectrum sequence."""
from math import pi
import numpy as np
import pypulseq as pp

# Define system
system = pp.Opts(
    rf_ringdown_time=20e-6,
    rf_dead_time=20e-6, 
    rf_raster_time=5e-8,
    block_duration_raster=5e-8
)

def constructor(rf_duration: float = 400e-6, time_bw_product: float = 8, adc_duration: float = 4e-3, pulse_type: str = "trap") -> pp.Sequence:
    
    seq = pp.Sequence(system=system)
    seq.set_definition("Name", "fid_spectrum")

    if pulse_type == "sinc":
        rf_90 = pp.make_sinc_pulse(system=system, flip_angle=pi / 2, duration=rf_duration, apodization=0.5, time_bw_product=time_bw_product)
    elif pulse_type == "block":
        rf_90 = pp.make_block_pulse(system=system, flip_angle=pi / 2, duration=rf_duration)
    elif pulse_type == "trap":
        rf_trap = np.full(250, fill_value=1, dtype=float)
        rf_trap[:100] = np.linspace(0, 1, 100)
        rf_trap[-100:] = np.linspace(1, 0, 100)
        rf_90 = pp.make_arbitrary_rf(signal=rf_trap, flip_angle=pi/2, system=system)
    else:
            raise ValueError("Invalid pulse_type. Choose 'sinc', 'block', or 'trap'.")
        
    adc = pp.make_adc(
        num_samples=1000,  # Is not taken into account atm
        duration=adc_duration,
        system=system,
    )


    seq.add_block(rf_90)
    seq.add_block(adc)

    # Check sequence timing in each iteration
    check_passed, err = seq.check_timing()
    if not check_passed:
        raise ValueError("Sequence timing check failed: ", err)

    return seq
