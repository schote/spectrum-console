"""Constructor for spin-echo-based frequency calibration sequence."""
from math import pi

import numpy as np
import pypulseq as pp

from console.utilities.sequences.system_settings import system

# Definition of constants
ADC_DURATION = 4e-3


def constructor(
    n_steps: int = 10,
    flip_angle_range=(pi / 4, 3 * pi / 2),
    repetition_time: float = 1000,
    echo_time: float = 12e-3,
    rf_duration: float = 400e-6,
    use_sinc: bool = False
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

    # Define flip angles
    flip_angles = np.linspace(flip_angle_range[0], flip_angle_range[1], n_steps, endpoint=True)

    for angle in flip_angles:

        if use_sinc:
            rf_90 = pp.make_sinc_pulse(system=system, flip_angle=angle, duration=rf_duration)
            rf_180 = pp.make_sinc_pulse(system=system, flip_angle=angle * 2, duration=rf_duration)
        else:
            rf_90 = pp.make_block_pulse(system=system, flip_angle=angle, duration=rf_duration)
            rf_180 = pp.make_block_pulse(system=system, flip_angle=angle * 2, duration=rf_duration)

        te_delay_1 = pp.make_delay(echo_time / 2 - rf_duration)
        te_delay_2 = pp.make_delay(echo_time / 2 - rf_duration / 2 - ADC_DURATION / 2)

        seq.add_block(rf_90)
        seq.add_block(te_delay_1)
        seq.add_block(rf_180)
        seq.add_block(te_delay_2)
        seq.add_block(adc)
        seq.add_block(pp.make_delay(repetition_time))

    return seq, flip_angles
