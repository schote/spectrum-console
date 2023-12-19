"""Spin-echo spectrum."""
# %%
# imports
import logging
import numpy as np
from math import pi
import matplotlib.pyplot as plt
from console.spcm_control.interface_acquisition_parameter import AcquisitionParameter, Dimensions
from console.spcm_control.acquisition_control import AcquistionControl
from console.spcm_control.interface_acquisition_data import AcquisitionData
from console.utilities.plot_unrolled_sequence import plot_unrolled_sequence
import console.utilities.sequences as sequences

# %%
# Create acquisition control instance
configuration = "../device_config.yaml"
acq = AcquistionControl(configuration_file=configuration, console_log_level=logging.INFO, file_log_level=logging.DEBUG)

# %%
# Construct and plot sequence
seq, flip_angles = sequences.se_tx_adjust.constructor(echo_time=12e-3, rf_duration=200e-6, n_steps=50, flip_angle_range=(pi/4, 3*pi/4), pulse_type="sinc")
# seq, flip_angles = sequences.fid_tx_adjust.constructor(rf_duration=200e-6, n_steps=50, flip_angle_range=(pi/4, 3*pi/4), pulse_type="sinc")


# Optional:
acq.seq_provider.from_pypulseq(seq)
seq_unrolled = acq.seq_provider.unroll_sequence(larmor_freq=2e6, grad_offset=Dimensions(0, 0, 0))
fig, ax = plot_unrolled_sequence(seq_unrolled)

# %%
flip_angle_array = []
amplitude_lists = []
# Larmor frequency:
f_0 = 2036468.75

# 10 measurement per flip angle
meas_per_angle = 10

for flip_angle in flip_angles:
    amplitude_list = []
    
    params = AcquisitionParameter(
        larmor_frequency=f_0,
        b1_scaling=4.5,
        num_averages=1,
        flip_angle=flip_angle,
    )

    for measurement in range(meas_per_angle):
        acq_data: AcquisitionData = acq.run(parameter=params, sequence=seq)

    # %%
        data = np.mean(acq_data.raw, axis=0)[0].squeeze()
        # FFT
        data_fft = np.fft.fftshift(np.fft.fft(np.fft.fftshift(data)))
        fft_freq = np.fft.fftshift(np.fft.fftfreq(data.size, acq_data.dwell_time))

        max_spec = np.max(np.abs(data_fft))
        # f_0_offset = fft_freq[np.argmax(np.abs(data_fft))]
        
        amplitude_list.append(max_spec)
        
    average_amplitude = np.mean(amplitude_list)

    flip_angle_array.append(flip_angle)
    amplitude_lists.append(amplitude_list)

    # Add information to acquisition data
    acq_data.add_info({
        "flip angle": flip_angle,
        "magnitude spectrum max": max_spec
    })

    print(f"Frequency spectrum max.: {max_spec}")
    print("Acquisition data shape: ", acq_data.raw.shape)
#%%
np.save("flip_angle_array.npy", flip_angle_array)
np.save("amplitude_lists.npy", amplitude_lists)

# Plot spectrum
# fig, ax = plt.subplots(1, 1, figsize=(10, 5))
# ax.plot(fft_freq, np.abs(data_fft))    
# ax.set_xlim([-20e3, 20e3])
# ax.set_ylim([0, max_spec*1.05])
# ax.set_ylabel("Abs. FFT Spectrum [a.u.]")
# _ = ax.set_xlabel("Frequency [Hz]")

# %%
"""Spin-echo spectrum."""
# %%
# imports
import logging
import numpy as np
from math import pi
import matplotlib.pyplot as plt
from console.spcm_control.interface_acquisition_parameter import AcquisitionParameter, Dimensions
from console.spcm_control.acquisition_control import AcquistionControl
from console.spcm_control.interface_acquisition_data import AcquisitionData
from console.utilities.plot_unrolled_sequence import plot_unrolled_sequence
import console.utilities.sequences as sequences

# %%
# Create acquisition control instance
configuration = "../device_config.yaml"
acq = AcquistionControl(configuration_file=configuration, console_log_level=logging.INFO, file_log_level=logging.DEBUG)

# %%
# Construct and plot sequence
seq, flip_angles = sequences.se_tx_adjust.constructor(echo_time=12e-3, rf_duration=200e-6, n_steps=50, flip_angle_range=(pi/4, 3*pi/4), pulse_type="sinc")
# seq, flip_angles = sequences.fid_tx_adjust.constructor(rf_duration=200e-6, n_steps=50, flip_angle_range=(pi/4, 3*pi/4), pulse_type="sinc")


# Optional:
acq.seq_provider.from_pypulseq(seq)
seq_unrolled = acq.seq_provider.unroll_sequence(larmor_freq=2e6, grad_offset=Dimensions(0, 0, 0))
fig, ax = plot_unrolled_sequence(seq_unrolled)

# %%
flip_angle_array = []
amplitude_lists = []
# Larmor frequency:
f_0 = 2036468.75

# 10 measurement per flip angle
meas_per_angle = 10

for flip_angle in flip_angles:
    amplitude_list = []
    
    params = AcquisitionParameter(
        larmor_frequency=f_0,
        b1_scaling=4.5,
        num_averages=1,
        flip_angle=flip_angle,
    )

    for measurement in range(meas_per_angle):
        acq_data: AcquisitionData = acq.run(parameter=params, sequence=seq)

    # %%
        data = np.mean(acq_data.raw, axis=0)[0].squeeze()
        # FFT
        data_fft = np.fft.fftshift(np.fft.fft(np.fft.fftshift(data)))
        fft_freq = np.fft.fftshift(np.fft.fftfreq(data.size, acq_data.dwell_time))

        max_spec = np.max(np.abs(data_fft))
        # f_0_offset = fft_freq[np.argmax(np.abs(data_fft))]
        
        amplitude_list.append(max_spec)
        
    average_amplitude = np.mean(amplitude_list)

    flip_angle_array.append(flip_angle)
    amplitude_lists.append(amplitude_list)

    # Add information to acquisition data
    acq_data.add_info({
        "flip angle": flip_angle,
        "magnitude spectrum max": max_spec
    })

    print(f"Frequency spectrum max.: {max_spec}")
    print("Acquisition data shape: ", acq_data.raw.shape)
#%%
np.save("flip_angle_array.npy", flip_angle_array)
np.save("amplitude_lists.npy", amplitude_lists)

# Plot spectrum
# fig, ax = plt.subplots(1, 1, figsize=(10, 5))
# ax.plot(fft_freq, np.abs(data_fft))    
# ax.set_xlim([-20e3, 20e3])
# ax.set_ylim([0, max_spec*1.05])
# ax.set_ylabel("Abs. FFT Spectrum [a.u.]")
# _ = ax.set_xlabel("Frequency [Hz]")

# %%
# Plot
fig, ax = plt.subplots(figsize=(10, 5))
ax.scatter(np.degrees(flip_angle_array), np.mean(amplitude_lists, axis=1), marker='o')
ax.set_xlabel('Flip-Winkel (°)')
ax.set_ylabel('Durchschnittliche Amplitude')
ax.set_title('Amplitude vs. Flip-Winkel')
plt.show()

flip_angle_max_amp = np.degrees(flip_angles[np.argmax(np.mean(amplitude_lists, axis=1))])
print("max. at flip angle: ", flip_angle_max_amp)
