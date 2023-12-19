# %%
"""Constructor for spin-echo-based frequency calibration sequence."""
from math import pi
import numpy as np
import pypulseq as pp
from console.utilities.sequences.system_settings import system
# %%

# Definition of constants
ADC_DURATION = 4e-3


def constructor(
    n_steps: int = 10,
    repetition_time: float = 1000,
    echo_time: float = 12e-3,
    rf_duration: float = 400e-6,
    flip_angle_range=(-pi/4, pi/4),
    pulse_type: str = "block",      
) -> tuple[pp.Sequence, np.ndarray]:
    """Construct transmit adjust sequence.

    Parameters
    ----------
    n_steps, optional
        Number of flip angles, by default 10
    tr, optional
        Repetition time in s, by default 1000
    te, optional
        Echo time in s, by default 12e-3

    Returns
    -------
        Pypulseq ``Sequence`` instance and flip angles in rad

    Raises
    ------
    ValueError
        Sequence timing check failed
    """
    seq = pp.Sequence(system=system)
    seq.set_definition("Name", "tx_adjust")
    
    adc = pp.make_adc(
        num_samples=1000,  # Is not taken into account atm
        duration=ADC_DURATION,
        system=system,
    )
    # seq.plot()

    # Define flip angles
    # flip_angles = np.linspace(start=(2 * pi) / n_steps, stop=2 * pi, num=n_steps, endpoint=True)
    flip_angles = np.linspace(flip_angle_range[0], flip_angle_range[1], n_steps, endpoint=True)

    for angle in flip_angles:
    
        if pulse_type == "sinc":
            rf_90 = pp.make_sinc_pulse(system=system, flip_angle=angle, duration=rf_duration, apodization=0.5)
            rf_180 = pp.make_sinc_pulse(system=system, flip_angle=angle*2, duration=rf_duration, apodization=0.5)

        elif pulse_type == "block":
            rf_90 = pp.make_block_pulse(system=system, flip_angle=angle, duration=rf_duration)
            rf_180 = pp.make_block_pulse(system=system, flip_angle=angle*2, duration=rf_duration)
        else:
                raise ValueError("Invalid pulse_type. Choose 'sinc' or 'block'.")
        

        te_delay_1 = pp.make_delay(echo_time / 2 - rf_duration - rf_90.ringdown_time - rf_180.dead_time)
        te_delay_2 = pp.make_delay(echo_time / 2 - rf_duration / 2 - rf_180.ringdown_time - ADC_DURATION/ 2 - adc.dead_time)

        seq.add_block(rf_90)
        seq.add_block(te_delay_1)
        seq.add_block(rf_180)
        seq.add_block(te_delay_2)
        seq.add_block(adc)
        seq.add_block(pp.make_delay(repetition_time))
        
        # Check sequence timing in each iteration
        check_passed, err = seq.check_timing()
        if not check_passed:
            raise ValueError("Sequence timing check failed: ", err)

    return seq, flip_angles
    
# %%
seq, _ = constructor()
seq.plot()
# %%