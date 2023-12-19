# %%
import os
import json
import numpy as np
import matplotlib.pyplot as plt


# %%
# window_width = 4000

def calculate_snr(data_fft, dwell_time, window_width=2000):
# def calculate_snr(data_fft, dwell_time):

    peak = np.max(np.abs(data_fft))
    fft_freq = np.fft.fftshift(np.fft.fftfreq(data_fft.shape[-1], dwell_time))

    half_width = int(window_width / 2)
    peak_position = np.argmax(np.abs(data_fft))
    left_window_idx = np.argmin(np.abs(fft_freq + fft_freq[peak_position] + half_width))
    right_window_idx = np.argmin(np.abs(fft_freq + fft_freq[peak_position] - half_width))

    noise = np.concatenate((data_fft[..., :left_window_idx], data_fft[..., right_window_idx:]))

    # Return snr in dB
    return 20 * np.log10(peak / np.mean(np.abs(noise)))

output_directories = [
    r'C:\Users\Jana0\OneDrive\Desktop\Bachelorarbeit\Frequenzkalibrierung Messdaten\Freq_Measurement\output_spectrum_sinc_0.0002_1',
    r'C:\Users\Jana0\OneDrive\Desktop\Bachelorarbeit\Frequenzkalibrierung Messdaten\Freq_Measurement\output_spectrum_sinc_0.0004_2',
    r'C:\Users\Jana0\OneDrive\Desktop\Bachelorarbeit\Frequenzkalibrierung Messdaten\Freq_Measurement\output_spectrum_block_0.0002_0',
]

results = {}

for output_directory in output_directories:
    matching_folders = np.load(os.path.join(output_directory, 'matching_folders.npy'), allow_pickle=True)

    larmor_frequencies_list = []
    detected_frequencies_list = []
    snr_values_list = []

    for folder_info in matching_folders:
        folder_name = folder_info['folder_name']
        folder_path = os.path.join(output_directory, folder_name)

        #load Data 
        raw_data_path = os.path.join(folder_path, 'raw_data.npy')
        meta_path = os.path.join(folder_path, 'meta.json')

        data = np.mean(np.load(raw_data_path), axis=0).squeeze()

        with open(meta_path, 'r') as f:
            meta_data = json.load(f)

        larmor_frequency = meta_data['acquisition_parameter']['larmor_frequency']
        larmor_frequencies_list.append(larmor_frequency)

        # FFT
        dwell_time = 5e-6
        data_fft = np.fft.fftshift(np.fft.fft(np.fft.fftshift(data), axis=-1))
        fft_freq = np.fft.fftshift(np.fft.fftfreq(data.shape[-1], dwell_time))

        # Find detected frequency
        f_0_offset = fft_freq[np.argmax(np.abs(data_fft))]
        detected_frequency = larmor_frequency - f_0_offset
        detected_frequencies_list.append(f_0_offset)

        
        snr_db = calculate_snr(data_fft, dwell_time)
        snr_values_list.append(snr_db)
        
    
    output_identifier = os.path.basename(output_directory)
    results[output_identifier] = {
        'larmor_frequencies': np.array(larmor_frequencies_list),
        'detected_frequencies': np.array(detected_frequencies_list),
        'snr_values': np.array(snr_values_list)
    }
    
    
#%%
np.save(os.path.join(output_directory, f'larmor_frequencies_{output_identifier}.npy'), np.array(larmor_frequencies_list))
np.save(os.path.join(output_directory, f'detected_frequencies_{output_identifier}.npy'), np.array(detected_frequencies_list))
np.save(os.path.join(output_directory, f'snr_values_{output_identifier}.npy'), np.array(snr_values_list))

# %%
# Plot SNR Window
plt.figure(figsize=(10, 6))
plt.plot(fft_freq, np.abs(data_fft.squeeze()))
plt.axvline(x=f_0_offset, color='r', linestyle='--', label='Detected Frequency')
plt.axvspan(f_0_offset - window_width/2, f_0_offset + window_width/2, alpha=0.3, color='green', label='Window')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Amplitude')
plt.legend()
plt.xlim([-20e3, 20e3])
plt.show()

print(f"Original Peak Position: {f_0_offset}")
print(f"Window Start: {f_0_offset - window_width/2}, Window End: {f_0_offset + window_width/2}")


# %%
plt.figure(figsize=(10, 6))
markers = ['o', 'x', '+']

for idx, (output_identifier, result_data) in enumerate(results.items()):
    plt.scatter(result_data['larmor_frequencies'], result_data['snr_values'], label=f'{output_identifier}', marker=markers[idx])

    # Calculate and print the average SNR for the current output directory
    avg_snr_values = np.mean(result_data['snr_values'])
    print(f"Avg SNR for {output_identifier}: {avg_snr_values:.2f} dB")

plt.xlabel('Larmor Frequency [Hz]')
plt.ylabel('Signal-to-Noise Ratio (SNR)')
plt.ylim(bottom=10, top=50)
plt.legend()
plt.grid(True)
plt.savefig(r'C:\Users\Jana0\OneDrive\Desktop\Bachelorarbeit\Frequenzkalibrierung Messdaten\Freq_Measurement\snr_plot_BW5000.png') 
plt.show()

print("SNR:", snr_db)
# %%
# Print SNR values for each measurement in the current output directory
for i, snr_db in enumerate(snr_values):
    print(f"SNR for Measurement {i+1}: {snr_db:.2f} dB")
    
# %%
# Plot: Detected Frequencies and Offsets
plt.figure(figsize=(10, 6))
markers = ['o', 'x', '+']
for idx, (output_identifier, result_data) in enumerate(results.items()):
    detected_frequencies = result_data['detected_frequencies']
    
    freq_range = np.linspace(-10000, +10000, 21, endpoint=True)
    plt.scatter(freq_range, detected_frequencies, label=f'{output_identifier}', marker=markers[idx])
    print("Detected Frequencies:", detected_frequencies)
    print("Offset", freq_range)
plt.xlabel('Offsets [Hz]')
plt.ylabel('Detected Frequencies [Hz]')
plt.yticks(np.arange(-60000, 11000, 5000))
plt.legend()
plt.grid(True)
plt.savefig(r'C:\Users\Jana0\OneDrive\Desktop\Bachelorarbeit\Frequenzkalibrierung Messdaten\Freq_Measurement\detected_frequency_plot_BW20000.png') 
plt.show()


# %%

