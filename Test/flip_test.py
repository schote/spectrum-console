"""Constructor for spin-echo spectrum sequence."""
# %%
from math import pi
import numpy as np
import pypulseq as pp
from console.utilities.sequences.system_settings import system
# %%
# Define system
system = pp.Opts(
    rf_ringdown_time=20e-6,
    rf_dead_time=20e-6, 
    rf_raster_time=5e-8,
    rf_dead_time = 100e-6,
    rf_ringdown_time = 100e-6,
    block_duration_raster=5e-8,
)

def constructor(rf_duration: float = 400e-6, adc_duration: float = 4e-3, tr = 5e-05, pulse_type: str = "sinc") -> pp.Sequence:
    
    seq = pp.Sequence(system=system)
    seq.set_definition("Name", "flip_test")
    
    # Define flip angles
    num_measurements = 50
    flip_angles = np.linspace(-45, 45, num_measurements)
    
    for angle in flip_angles:
    
        if pulse_type == "sinc":
            rf_90 = pp.make_sinc_pulse(system=system, flip_angle=angle, duration=rf_duration, apodization=0.5)
            rf_180 = pp.make_sinc_pulse(system=system, flip_angle=angle*2, duration=rf_duration, apodization=0.5)

        elif pulse_type == "block":
            rf_90 = pp.make_block_pulse(system=system, flip_angle=angle, duration=rf_duration)
            rf_180 = pp.make_block_pulse(system=system, flip_angle=angle*2, duration=rf_duration)
        else:
                raise ValueError("Invalid pulse_type. Choose 'sinc', 'block', or 'trap'.")
        
        adc = pp.make_adc(
        num_samples=1000,  # Is not taken into account atm
        duration=adc_duration,
        system=system,
        )
        
        te = 20e-3
        
        delay_1 = pp.make_delay(te / 2 - rf_duration - rf_90.ringdown_time - rf_180.dead_time)
        delay_2 = pp.make_delay(te / 2 - rf_duration / 2 - rf_180.ringdown_time - adc_duration/ 2 - adc.dead_time)
        
        seq.add_block(rf_90)
        seq.add_block(delay_1)
        seq.add_block(rf_180)
        seq.add_block(delay_2)
        seq.add_block(adc)
        seq.add_block(pp.make_delay(tr))

    # Check sequence timing in each iteration
    check_passed, err = seq.check_timing()
    if not check_passed:
        raise ValueError("Sequence timing check failed: ", err)

    return seq, flip_angles
