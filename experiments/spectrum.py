"""Spin-echo spectrum."""
# %%
# imports
import logging

import matplotlib.pyplot as plt
import numpy as np

import console.utilities.sequences as sequences
from console.spcm_control.acquisition_control import AcquistionControl
from console.spcm_control.interface_acquisition_data import AcquisitionData
from console.spcm_control.interface_acquisition_parameter import AcquisitionParameter, Dimensions
from console.utilities.plot_unrolled_sequence import plot_unrolled_sequence
from console.utilities.snr import signal_to_noise_ratio

# %%
# Create acquisition control instance
configuration = "../device_config.yaml"
acq = AcquistionControl(configuration_file=configuration, console_log_level=logging.INFO, file_log_level=logging.DEBUG)

# %%
# Construct and plot sequence
seq = sequences.se_spectrum.constructor(echo_time=10e-3, adc_duration=4e-3, rf_duration=200e-6, use_sinc=False)

# Optional:
acq.seq_provider.from_pypulseq(seq)
seq_unrolled = acq.seq_provider.unroll_sequence(larmor_freq=2e6, grad_offset=Dimensions(0, 0, 0))
fig, ax = plot_unrolled_sequence(seq_unrolled)

# %%
# Larmor frequency:
# f_0 = 2038555   # Berlin system
f_0 = 2038550
# f_0 = 1964690.0   # Leiden system

# Define acquisition parameters
params = AcquisitionParameter(
    larmor_frequency=f_0,
    b1_scaling=2.43, # 8 cm phantom
    # b1_scaling=6.3,
    decimation=200,
    # num_averages=10,
    # averaging_delay=2,
)

# Perform acquisition
acq_data: AcquisitionData = acq.run(parameter=params, sequence=seq)
data = np.mean(acq_data.raw, axis=0).squeeze()

# %%
# FFT
data_fft = np.fft.fftshift(np.fft.fft(np.fft.fftshift(data)))
fft_freq = np.fft.fftshift(np.fft.fftfreq(data.size, acq_data.dwell_time))

snr = round(signal_to_noise_ratio(data_fft, dwell_time=acq_data.dwell_time, window_width=3000), 4)

# Print peak height and center frequency
max_spec = np.max(np.abs(data_fft))
f_0_offset = fft_freq[np.argmax(np.abs(data_fft))]

print(f"Frequency offset [Hz]: {f_0_offset}, new frequency f0 [Hz]: {f_0 - f_0_offset}")
print(f"Frequency spectrum max.: {max_spec}")
print("Acquisition data shape: ", acq_data.raw.shape)
print(f"SNR: {snr} dB")

# Plot spectrum
fig, ax = plt.subplots(1, 1, figsize=(10, 5))
ax.plot(fft_freq, np.abs(data_fft))
ax.set_xlim([-25e3, 25e3])
ax.set_ylim([0, max_spec*1.05])
ax.set_ylabel("Abs. FFT Spectrum [a.u.]")
_ = ax.set_xlabel("Frequency [Hz]")

# %%
# Save

# Preamp comparison
model = "china_preamp"
# model = "wenteq_ABL0100-00-6010_1"
# model = "wenteq_ABL0100-00-6010_2"
# model = "wenteq_ABL0050-00-4510"
# model = "minicircuit_ZFL-500LN"
# model = "no-preamp"

# Add information to acquisition data
acq_data.add_info({
    "true f0": f_0 - f_0_offset,
    "magnitude spectrum max": max_spec,
    "snr": snr,
    "preamp": model,
})

acq_data.write(user_path=f"/home/schote01/data/preamp-comparison/{model}/")

# %%
del acq
# %%
