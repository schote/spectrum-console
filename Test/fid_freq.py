# %%
from math import pi
import pypulseq as pp
import numpy as np
import matplotlib.pyplot as plt

# %%
def plot_and_fft(signal, system, title):

    rf_fft = np.fft.fftshift(np.fft.fft(signal))
    fft_freq_rf = np.fft.fftshift(np.fft.fftfreq(len(signal), 1/fs))

    plt.figure(figsize=(12, 4))

    plt.subplot(1, 2, 1)  
    plt.plot(signal)
    plt.title(f'{title} - Zeitbereich')
    plt.xlabel('Zeit')
    plt.ylabel('Amplitude')

    plt.subplot(1, 2, 2) 
    plt.plot(fft_freq_rf, np.abs(rf_fft))
    plt.title(f'{title} - Frequenzbereich')
    plt.xlabel('Frequenz (Hz)')
    plt.ylabel('Amplitude')

    plt.show()
# %%
# Define system
system = pp.Opts(
    rf_ringdown_time=50e-6,    
    rf_dead_time=20e-6, 
    rf_raster_time=5e-8,
    block_duration_raster=5e-8
)

# Parameters
rf_duration = 250e-6
num_samples = 5000
adc_duration = 4e-3 

fs = 8000 # Abtastrate


# Zeitvektor
t = np.linspace(0, rf_duration, num_samples, endpoint=False)

# Block-Signal
rf_block = np.zeros(num_samples)
rf_block[200:801] = 1

# Trapez-Signal
rf_trap = np.full(250, fill_value=1, dtype=float)
rf_trap[:50] = np.linspace(0, 1, 50) #**2
rf_trap[-50:] = np.linspace(1, 0, 50) #**2

# Chirp parameter
1900000.0000
chirp_start_freq = 1800000.0000
chirp_stop_freq = 2200000.0000  
# chirp_start_freq = 1000000.000  # Start frequency in Hz
# chirp_stop_freq = 3000000.000   # Stopp frequency in Hz
# chirp_waveform = np.sin(2 * pi * t * (chirp_start_freq + 
#                                       (chirp_stop_freq - chirp_start_freq) 
#                                       * t / rf_duration))
chirp_waveform = np.exp(1j * (2 * pi * chirp_start_freq * t + pi 
                              * (chirp_stop_freq - chirp_start_freq) 
                              * t**2 / rf_duration))

# Block-Pulse
rf_pulse_block = pp.make_arbitrary_rf(
    signal=rf_block,
    flip_angle=pi/2,
    time_bw_product=4,
    system=system,
)

# Trapez-Pulse
rf_pulse_trap = pp.make_arbitrary_rf(
    signal=rf_trap,
    flip_angle=pi/2,
    system=system,
)

# Chirp-Pulse
rf_pulse_chirp = pp.make_arbitrary_rf(
    signal=chirp_waveform,
    flip_angle=pi/2,
    system=system,
)

# Sinc-Puls
rf_pulse_sinc = pp.make_sinc_pulse(
    duration=rf_duration,
    flip_angle=pi/2,
    system=system,
)

# Gauss-Puls 
rf_pulse_gauss = pp.make_gauss_pulse(
    duration=rf_duration,
    flip_angle=pi/2,
    system=system,
)
# %%
plot_and_fft(rf_pulse_block.signal, system, 'Block-Puls')
# %%
plot_and_fft(rf_pulse_trap.signal, system, 'Trapez-Puls')
# %%
plot_and_fft(rf_pulse_chirp.signal, system, 'Chirp-Puls')
# %%
plot_and_fft(rf_pulse_sinc.signal, system, 'Sinc-Puls')
# %%
# plot_and_fft(rf_pulse_gauss.signal, system, 'Gauss-Puls')

# %%
#Bandbreite
def calculate_bandwidth(signal, fs, threshold=0.1):
    
    fft_signal = np.fft.fftshift(np.fft.fft(signal))
    # peak_index = np.argmax(np.abs(fft_signal))
    threshold_value = threshold * np.max(np.abs(fft_signal))
    above_threshold_index = np.where(np.abs(fft_signal) > threshold_value)[0]
    bandwidth = fs * (above_threshold_index[-1] - above_threshold_index[0]) / len(signal)
    return bandwidth

bandwidth_block = calculate_bandwidth(rf_pulse_block.signal, fs)
bandwidth_trap = calculate_bandwidth(rf_pulse_trap.signal, fs)
bandwidth_chirp = calculate_bandwidth(rf_pulse_chirp.signal, fs)
bandwidth_sinc = calculate_bandwidth(rf_pulse_sinc.signal, fs)
# bandwidth_gauss = calculate_bandwidth(rf_pulse_gauss.signal, fs)


print(f'Block-Puls - Bandbreite: {bandwidth_block} Hz')
print(f'Trapez-Puls - Bandbreite: {bandwidth_trap} Hz')
print(f'Chirp-Puls - Bandbreite: {bandwidth_chirp} Hz')
print(f'Sinc-Puls - Bandbreite: {bandwidth_sinc} Hz')
# print(f'Gauss-Puls - Bandbreite: {bandwidth_gauss} Hz')

# %%
# seq.write('../Test/se_rf_flip.seq', False)
