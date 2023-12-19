# %%
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# %%
output_directory = r'C:\Users\Jana0\OneDrive\Desktop\Bachelorarbeit\Frequenzkalibrierung Messdaten\Freq_Measurement\output_spectrum_block_5e-05_0'

matching_folders = np.load(os.path.join(output_directory, 'matching_folders.npy'), allow_pickle=True)

larmor_frequencies_list = []
detected_frequencies_list = []
snr_values_list = []

def calculate_snr(data_fft, dwell_time, window_width=4000):
    peak = np.max(np.abs(data_fft))
    fft_freq = np.fft.fftshift(np.fft.fftfreq(data_fft.shape[-1], dwell_time))

    # Define start and end indices of the window
    half_width = int(window_width / 2)
    peak_position = np.argmax(np.abs(data_fft))
    left_window_idx = np.argmin(np.abs(fft_freq + fft_freq[peak_position] + half_width))
    right_window_idx = np.argmin(np.abs(fft_freq + fft_freq[peak_position] - half_width))

    # Extract pure noise from outside the window containing the peak
    noise = np.concatenate((data_fft[..., :left_window_idx], data_fft[..., right_window_idx:]))

    # Return snr in dB
    return 20 * np.log10(peak / np.mean(np.abs(noise)))

# Iterate through all measurements
for idx, folder_info in enumerate(matching_folders):
    folder_name = folder_info['folder_name']
    folder_path = os.path.join(output_directory, folder_name)

    # Load data and meta information
    raw_data_path = os.path.join(folder_path, 'raw_data.npy')
    meta_path = os.path.join(folder_path, 'meta.json')

    data = np.mean(np.load(raw_data_path), axis=0).squeeze()

    with open(meta_path, 'r') as f:
        meta_data = json.load(f)

    larmor_frequency = meta_data['acquisition_parameter']['larmor_frequency']
    larmor_frequencies_list.append(larmor_frequency)

    # FFT
    dwell_time = 10e-6
    data_fft = np.fft.fftshift(np.fft.fft(np.fft.fftshift(data), axis=-1))
    fft_freq = np.fft.fftshift(np.fft.fftfreq(data.shape[-1], dwell_time))

    # Find detected frequency
    f_0_offset = fft_freq[np.argmax(np.abs(data_fft))]
    detected_frequency = larmor_frequency - f_0_offset
    detected_frequencies_list.append(f_0_offset)

    # Calculate SNR using the separate function
    snr_db = calculate_snr(data_fft, dwell_time)
    snr_values_list.append(snr_db)

    larmor_frequencies = np.array(larmor_frequencies_list)
    detected_frequencies = np.array(detected_frequencies_list)
    snr_values = np.array(snr_values_list)
    max_spec = np.max(np.abs(data_fft))
    
    # Plot Spectrum
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.plot(fft_freq, np.abs(data_fft.squeeze()))

    ax.set_xlim([-20e3, 20e3])
    ax.set_ylim([-20, 1600])
    ax.set_ylabel("Abs. FFT data_fft [a.u.]")
    ax.set_xlabel("Frequency [Hz]")
    plt.show()

    print("lamor:", larmor_frequency)
    print("detected:", detected_frequency)
    print(f"Frequency spectrum max.: {max_spec}")
# %%
# Plot SNR
plt.scatter(larmor_frequencies, snr_values, label='SNR', marker='o', color='green')
plt.ylabel("Signal-to-Noise Ratio (SNR)")
plt.xlabel("Larmor Frequency [Hz]")
plt.legend()
plt.savefig(os.path.join(output_directory, 'snr_plot.png'))
plt.show()
# %%
# Plot Detected Frequencies
freq_range = np.linspace(-10000, +10000, 21, endpoint=True)

plt.scatter(freq_range, detected_frequencies_list, label='Detected Frequencies', marker='x', color='blue')
plt.ylabel("Detected Frequency [Hz]")
plt.xlabel("Measurement Index")
plt.legend()
plt.savefig(os.path.join(output_directory, 'detected_frequency_plot_all.png'))
plt.show()

# %%
