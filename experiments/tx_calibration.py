"""Transmit power calibration (flip angle)."""
# %%
# imports
import logging
import numpy as np
from math import pi
import matplotlib.pyplot as plt
from console.spcm_control.interface_acquisition_parameter import AcquisitionParameter, Dimensions
from console.spcm_control.acquisition_control import AcquistionControl
from console.spcm_control.interface_acquisition_data import AcquisitionData
import console.utilities.sequences as sequences


# %%
# Create acquisition control instance
configuration = "../device_config.yaml"
acq = AcquistionControl(configuration_file=configuration, console_log_level=logging.INFO, file_log_level=logging.DEBUG)

# %%
# Construct and plot sequence
seq, flip_angles = sequences.se_tx_adjust.constructor(echo_time=12e-3, rf_duration=200e-6, repetition_time=4, n_steps=50, flip_angle_range=(pi/4, 3*pi/2), pulse_type="block")
# seq, flip_angles = sequences.fid_tx_adjust.constructor(rf_duration=200e-6, repetition_time = 4, n_steps=50, flip_angle_range=(pi/4, 3*pi/2), pulse_type="block")

# %%
# Larmor frequency:
f_0 = 2033500.0
# f_0 = 1964690.0 # leiden

# Define acquisition parameters
params = AcquisitionParameter(
    larmor_frequency=f_0,
    b1_scaling=2.42, # 8 cm phantom
    decimation=200,
)

# Perform acquisition
acq_data: AcquisitionData = acq.run(parameter=params, sequence=seq)

# %%
# FFT
data = np.mean(acq_data.raw, axis=0)[0, ...]
data = np.abs(np.fft.fftshift(np.fft.fft(np.fft.fftshift(data), axis=-1)))

center_window = 100
window_start = int(data.shape[-1]/2-center_window/2)
peak_windows = data[:, window_start:window_start+center_window]
peaks = np.max(peak_windows, axis=-1)

fig, ax = plt.subplots(1, 1, figsize=(10, 6))
ax.scatter(np.degrees(flip_angles), peaks)
ax.set_ylabel("Amplitude [a.u.]")
ax.set_xlabel("Flip angle [°]")


flip_angle_max_amp = np.degrees(flip_angles[np.argmax(peaks)])
print("True max. at flip angle: ", flip_angle_max_amp)
factor = flip_angle_max_amp / 90
print("Scale B1 by: ", factor)

# %%

acq_data.add_info({
    "flip_angles": list(flip_angles),
    "peaks": list(peaks),
})

# %%
acq_data.write(save_unprocessed=False)

# %%
del acq
# %%

