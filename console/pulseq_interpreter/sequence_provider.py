"""Sequence provider class."""

import numpy as np
from pypulseq.opts import Opts
from pypulseq.Sequence.sequence import Sequence
from scipy.signal import resample


class SequenceProvider(Sequence):
    """Sequence provider class.

    This object is inherited from pulseq sequence object, so that all methods of the
    pypulseq ``Sequence`` object can be accessed.

    The main functionality of the ``SequenceProvider`` is to unroll a given pulseq sequence.
    Usually the first step is to read a sequence file. The unrolling step can be achieved using
    the ``unroll_sequence()`` function.

    Example
    -------
    >>> seq = SequenceProvider()
    >>> seq.read("./seq_file.seq")
    >>> sqnc, gate, total_samples = seq.unroll_sequence()
    """

    def __init__(
        self,
        # larmor_frequency: float = 2e6,
        spcm_sample_rate: float = 1 / 20e6,
        rf_double_precision: bool = True,
        grad_to_volt: float = 1,
        rf_to_volt: float = 1,
        system: Opts = Opts(),
    ):
        """Init function for sequence provider class."""
        super().__init__(system=system)

        self.grad_to_volt = grad_to_volt
        self.rf_to_volt = rf_to_volt

        self.spcm_freq = 1 / spcm_sample_rate
        self.spcm_sample_rate = spcm_sample_rate
        self.larmor_freq = self.system.B0 * self.system.gamma

        self.dtype = np.double if rf_double_precision else np.single

        self.carrier_time: np.ndarray | None = None
        self.carrier: np.ndarray | None = None

    def precalculate_carrier(self) -> None:
        """Pre-calculation of carrier signal for the longest occurring RF event.
        Each RF event reuses the pre-calculated signal.
        Dependent on the specific RF event it might be truncated and modulated.
        """
        rf_durations = []
        for k in self.block_events.keys():
            if (block := self.get_block(k)).rf:
                rf_durations.append(block.rf.shape_dur)

        if len(rf_durations) > 0:
            rf_dur_max = max(rf_durations)
            self.carrier_time = np.arange(start=0, stop=rf_dur_max, step=self.spcm_sample_rate, dtype=self.dtype)
            self.carrier = np.exp(2j * np.pi * self.larmor_freq * self.carrier_time)

    def calculate_rf(self, rf_block, num_total_samples: int) -> np.ndarray:
        """Calculates RF sample points to be played by TX card.

        Parameters
        ----------
        rf_block
            Pulseq RF block

        Returns
        -------
            List of RF samples

        Raises
        ------
        AttributeError
            Invalid RF block
        """
        if not rf_block.type == "rf":
            raise AttributeError("Block is not a valid RF block.")

        if self.carrier_time is None:
            raise RuntimeError("Missing precalculated carrier time raster.")

        # TODO: Take into account the phase starting point depending on the end-time of the last RF (!)

        # Calculate zero filling for RF delay
        delay = np.zeros(int(rf_block.delay / self.spcm_sample_rate), dtype=self.dtype)
        # Zero filling for RF ringdown (maximum of ringdown time defined in RF event and system)
        ringdown_dur = max(self.system.rf_ringdown_time, rf_block.ringdown_time)
        ringdown_time = np.zeros(int(ringdown_dur / self.spcm_sample_rate), dtype=self.dtype)
        # Zero filling for ADC dead-time (maximum of dead time defined in RF event and system)
        dead_dur = max(self.system.rf_dead_time, rf_block.dead_time)
        dead_time = np.zeros(int(dead_dur / self.spcm_sample_rate), dtype=self.dtype)

        # Calculate the number of shape sample points
        num_samples = int(rf_block.shape_dur / self.spcm_sample_rate)

        # Calculate the static phase offset, defined in RF pulse
        phase_offset = np.exp(1j * rf_block.phase_offset)

        # Resampling of complex envelope
        envelope = resample(rf_block.signal, num=num_samples)

        # Calcuate modulated RF signal with precalculated carrier and phase offset
        # >> Precalculating the exponential function saves about 200ms for TSE sequence
        # signal = (envelope * self.carrier[:num_samples] * phase_offset).real

        # Update: Only precalculate carrier time array, calculate carriere here to take into account the
        # frequency offset of an RF block event
        carrier = np.exp(2j * np.pi * (self.larmor_freq + rf_block.freq_offset) * self.carrier_time[:num_samples])
        signal = (envelope * carrier * phase_offset).real

        # Combine signal from delays and rf
        rf_pulse = np.concatenate((delay, signal, ringdown_time, dead_time))

        if (num_signal_samples := len(rf_pulse)) < num_total_samples:
            # Zero-fill rf signal
            rf_pulse = np.concatenate((rf_pulse, np.zeros(num_total_samples - num_signal_samples, dtype=self.dtype)))
        elif num_signal_samples > num_total_samples:
            raise ArithmeticError("Number of signal samples exceeded the total number of block samples.")

        return rf_pulse * self.rf_to_volt

    def calculate_gradient(self, block, num_total_samples: int, amp_offset: float = 0.0) -> np.ndarray:
        """Calculate spectrum-card sample points of a gradient waveform.

        Parameters
        ----------
        block
            Gradient block from sequence, type must be grad or trap
        num_total_samples
            Total number of block samples points to verify calculation
        amp_offset, optional
            Amplitude offset, last value of last gradient, by default 0.

        Returns
        -------
            List of gradient waveform values

        Raises
        ------
        AttributeError
            Block type is not grad or trap
        ArithmeticError
            Number of calculated sample points is greater then number of block sample points
        """
        # Both gradient types have a delay
        # delay = [amp_offset] * int(block.delay/self.spcm_sample_rate)
        delay = np.full(int(block.delay / self.spcm_sample_rate), fill_value=amp_offset, dtype=float)

        if block.type == "grad":
            # Arbitrary gradient waveform, interpolate linearly
            waveform = np.interp(
                x=np.linspace(block.tt[0], block.tt[-1], int(block.shape_dur / self.spcm_sample_rate)),
                xp=block.tt,
                fp=block.waveform + amp_offset,
            )
            # gradient = delay + list(waveform)
            gradient = np.concatenate((delay, waveform))

        elif block.type == "trap":
            # Trapezoidal gradient, combine resampled rise, flat and fall sections
            rise = np.linspace(amp_offset, amp_offset + block.amplitude, int(block.rise_time / self.spcm_sample_rate))
            flat = np.full(int(block.flat_time / self.spcm_sample_rate), fill_value=block.amplitude + amp_offset)
            fall = np.linspace(amp_offset + block.amplitude, amp_offset, int(block.fall_time / self.spcm_sample_rate))
            gradient = np.concatenate((delay, rise, flat, fall))

        else:
            raise AttributeError("Block is not a valid gradient block")

        # TODO: Is this a valid assumption? Gradients are zero-filled at the end?
        if (num_gradient_samples := len(gradient)) < num_total_samples:
            # gradient += [gradient[-1]] * (num_total_samples-num_gradient_samples)
            np.concatenate((gradient, np.full(num_total_samples - num_gradient_samples, fill_value=gradient[-1])))
        elif num_gradient_samples > num_total_samples:
            raise ArithmeticError("Number of gradient samples exceeded the total number of block samples.")

        return gradient * self.grad_to_volt

    def add_adc_gate(self, block, gate: np.ndarray) -> None:
        """Adds ADC gate signal inplace to gate array.

        Parameters
        ----------
        block
            ADC event of sequence block.
        gate
            Gate array, predefined by zeros. If ADC event is present, the corresponding range is set to one.
        """
        delay = int(block.delay / self.spcm_sample_rate)
        # dead_dur = max(self.system.adc_dead_time, block.dead_time)
        # dead_time = int(dead_dur / self.spcm_sample_rate)
        adc_len = int(block.num_samples * block.dwell / self.spcm_sample_rate)
        gate[delay : delay + adc_len] = 1

    def unroll_sequence(self) -> (np.ndarray, int):
        """Unroll a read sequence object.

        Returns
        -------
            List of lists, block-wise calculated sample points in correct order for spectrum card
            and total number of sequence sample points

        Raises
        ------
        AttributeError
            No sequence loaded
        """
        print("Unrolling sequnce...")

        if len(self.block_events) == 0:
            raise AttributeError("No sequence loaded.")

        # Pre-calculate the carrier signal to save computation time
        self.precalculate_carrier()

        # Get all blocks in a list and pre-calculate number of sample points per block
        # to allocate empty sequence array.
        blocks = [self.get_block(k) for k in list(self.block_events.keys())]
        samples_per_block = [int(block.block_duration / self.spcm_sample_rate) for block in blocks]
        _seq = [np.empty(4 * n) for n in samples_per_block]  # empty list of list, 4 channels => 4 times n_samples
        _adc = [np.zeros(n) for n in samples_per_block]

        # Last value of last block is added per channel to the gradient waveform as an offset value.
        # This is needed, since gradients must not be zero at the end of a block.
        gx_const = 0
        gy_const = 0
        gz_const = 0

        # Count the total number of sample points
        sample_count = 0

        # for k, (n_samples, block) in tqdm(enumerate(zip(samples_per_block, blocks))):
        for k, (n_samples, block) in enumerate(zip(samples_per_block, blocks)):
            sample_count += n_samples

            # Calculate rf events of current block, zero-fill channels if not defined
            rf_tmp = self.calculate_rf(block.rf, n_samples) if block.rf else np.zeros(n_samples)

            # TODO: Remember the phase of the last RF signal sample
            # => defines starting point for next RF event by adding a phase offset

            # Calculate gradient events of the current block, zero-fill channels if not defined
            gx_tmp = self.calculate_gradient(block.gx, n_samples, gx_const) if block.gx else np.zeros(n_samples)
            gy_tmp = self.calculate_gradient(block.gy, n_samples, gy_const) if block.gy else np.zeros(n_samples)
            gz_tmp = self.calculate_gradient(block.gz, n_samples, gz_const) if block.gz else np.zeros(n_samples)

            _seq[k] = np.stack((rf_tmp, gx_tmp, gy_tmp, gz_tmp)).flatten(order="F")

            if block.adc:
                self.add_adc_gate(block.adc, _adc[k])

        return _seq, _adc, sample_count