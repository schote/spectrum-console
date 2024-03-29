"""Interface class for an unrolled sequence."""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class UnrolledSequence:
    """Unrolled sequence interface.

    This interface is used to share the unrolled sequence between the
    different components like TxEngine, SequenceProvider and AcquisitionControl.
    An unrolled sequence is generated by a `SequenceProvider()` instance using the
    `unroll_sequence` function.
    """

    seq: list
    """Replay data as int16 values in a list of numpy arrays. The sequence data already
    contains the digital adc and unblanking signals in the channels gx and gy."""

    adc_gate: list
    """ADC gate signal in binary logic where 0 corresponds to ADC gate off and 1 to ADC gate on."""
    rf_unblanking: list
    """Unblanking signal for the RF power amplifier (RFPA) in binary logic. 0 corresponds to blanking state
    and 1 to unblanking state."""

    sample_count: int
    """Total number of samples per channel."""

    gpa_gain: list[float]
    """The gradient waveforms in pulseq are defined in Hz/m.
    The translation to mV is calculated by 1e3 / (gyro * gpa_gain * grad_efficiency).
    The gpa gain is given in V/A and accounts for the voltage required to generate an output of 1A.
    The gyromagnetic ratio defined by 42.58e6 MHz/T."""

    gradient_efficiency: list[float]
    """The gradient waveforms in pulseq are defined in Hz/m.
    The translation to mV is calculated by 1e3 / (gyro * gpa_gain * grad_efficiency).
    The gradient efficiency is given in mT/m/A and accounts for the gradient field which is generated per 1A.
    The gyromagnetic ratio defined by 42.58e6 MHz/T."""

    rf_to_mvolt: float
    """If sequence values are given as float values, they can be interpreted as output voltage [mV] directly.
    This conversion factor represents the scaling from original pulseq RF values [Hz] to card output voltage."""

    dwell_time: float
    """Dwell time of the spectrum card replay data (unrolled sequence).
    Defines the distance in time between to sample points.
    Note that this dwell time does not correlate to the larmor frequecy. Due to the sampling theorem
    `dwell_time < 1/(2*larmor_frequency)` must be satisfied. Usually a higher factor is chosen."""

    larmor_frequency: float
    """Larmor frequency of the MR scanner which defines the frequency of the RF pulse carrier signal."""

    duration: float
    """Total duration of the unrolled sequence in s."""

    adc_count: int
    """Number of adc events in the sequence."""
