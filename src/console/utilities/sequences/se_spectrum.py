"""Constructor for spin-echo spectrum sequence."""
from math import pi
import numpy as np
import pypulseq as pp

from console.utilities.sequences.system_settings import system

# Definition of constants
ADC_DURATION = 4e-3


def constructor(echo_time: float = 12e-3, rf_duration: float = 400e-6, time_bw_product: float = 8, pulse_type: str = "trap") -> pp.Sequence:
    
    """Construct spin echo spectrum sequence.

    Parameters
    ----------
    te, optional
        Echo time in s, by default 12e-3
    rf_duration, optional
        RF duration in s, by default 400e-6

    Returns
    -------
        Pypulseq ``Sequence`` instance

    Raises
    ------
    ValueError
        Sequence timing check failed
    """
    seq = pp.Sequence(system=system)
    seq_name = f"se_spectrum_{pulse_type}"
    seq.set_definition("Name", seq_name)

    if pulse_type == "sinc":
        rf_90 = pp.make_sinc_pulse(system=system, flip_angle=pi / 2, duration=rf_duration, apodization=0.5, time_bw_product=time_bw_product)
        rf_180 = pp.make_sinc_pulse(system=system, flip_angle=pi, duration=rf_duration, apodization=0.5, time_bw_product=time_bw_product)

    elif pulse_type == "block":
        rf_90 = pp.make_block_pulse(system=system, flip_angle=pi / 2, duration=rf_duration)
        rf_180 = pp.make_block_pulse(system=system, flip_angle=pi, duration=rf_duration)

    elif pulse_type == "trap":
        rf_trap = np.full(250, fill_value=1, dtype=float)
        rf_trap[:50] = np.linspace(0, 1, 50)
        rf_trap[-50:] = np.linspace(1, 0, 50)
        rf_90 = pp.make_arbitrary_rf(signal=rf_trap, flip_angle=pi/2, time_bw_product=time_bw_product, system=system)
        rf_180 = pp.make_arbitrary_rf(signal=rf_trap, flip_angle=pi, time_bw_product=time_bw_product, system=system)
    else:
            raise ValueError("Invalid pulse_type. Choose 'sinc', 'block', or 'trap'.")
        
    adc = pp.make_adc(
        num_samples=1000,  # Is not taken into account atm
        duration=ADC_DURATION,
        system=system,
    )

    te_delay_1 = pp.make_delay(echo_time / 2 - rf_duration)
    te_delay_2 = pp.make_delay(echo_time / 2 - rf_duration / 2 - ADC_DURATION / 2)

    seq.add_block(rf_90)
    seq.add_block(te_delay_1)
    seq.add_block(rf_180)
    seq.add_block(te_delay_2)
    seq.add_block(adc)

    # Check sequence timing in each iteration
    check_passed, err = seq.check_timing()
    if not check_passed:
        raise ValueError("Sequence timing check failed: ", err)

    return seq
