# %%
from math import pi
import pypulseq as pp
import numpy as np
import matplotlib.pyplot as plt

# %%
# Define system
system = pp.Opts(
    rf_ringdown_time=50e-6,    
    rf_dead_time=20e-6, 
    rf_raster_time = 5e-8,
    block_duration_raster = 5e-8
)
seq = pp.Sequence(system)

# Parameters
rf_duration = 250e-6
num_samples = 5000
adc_duration = 4e-3 
# te = 20e-3
# Larmor frequency: f_0 = 2037729.6875
# %%
## 90 degree block pulse
rf_pulse = pp.make_block_pulse(
    flip_angle=pi/2,              
    duration=rf_duration,     
    system=system,
)
# %%
# Trapez
rf_trap = np.full(1000, fill_value=1, dtype=float)
rf_trap[:200] = np.linspace(0, 1, 200)
rf_trap[-200:] = np.linspace(1, 0, 200)

# # # Create arbitrary RF pulse using make_arbitrary
rf_pulse = pp.make_arbitrary_rf(
    signal = rf_trap,
    flip_angle=pi/2,
    system=system,
    use = 'excitation'
)
# %%
# # Chirp parameter
# chirp_start_freq = 2037000.000 # Start frequency in Hz
# chirp_stop_freq = 2039000.000  # Stopp frequency in Hz
chirp_start_freq = 1000000.000 # Start frequency in Hz
chirp_stop_freq = 3000000.000  # Stopp frequency in Hz

t = np.linspace(0, rf_duration, num_samples, endpoint=False)
chirp_waveform = np.cos(2 * pi * t * (chirp_start_freq + 
                                      (chirp_stop_freq - chirp_start_freq) 
                                      * t / rf_duration))

# chirp pulse
rf_pulse = pp.make_arbitrary_rf(
    signal=chirp_waveform,
    flip_angle=pi/2,
    system=system,
)
# %%
# ADC event
adc = pp.make_adc(
    num_samples=num_samples,
    duration=adc_duration, 
    system=system
)

seq.add_block(rf_pulse)
seq.add_block(adc)
# %%
seq.plot()
# %%
# # FFT
fs = 5000  # Abtastrate (Hz)
rf_signal = rf_pulse.signal

rf_fft = np.fft.fftshift(np.fft.fft(rf_signal)) #Amplitude 
fft_freq_rf = np.fft.fftshift(np.fft.fftfreq(len(rf_signal), 1/fs)) #Zeitachse
# %%
#Blockpuls
# block_pulse = np.zeros(1000)
# block_pulse[200:801] = 1
# spectrum = np.fft.fftshift(np.fft.fft(np.fft.fftshift(rf_signal)))
# %%
# fig, ax = plt.subplots(1, 2)
# ax[0].plot(block_pulse)
# ax[1].plot(spectrum)

# %%
# RF-Puls
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)  
plt.plot(rf_signal)
plt.title('RF-Puls')
plt.xlabel('Zeit')
plt.ylabel('Amplitude')
# %%
# Frequenzspektrum
plt.subplot(1, 2, 2) 
plt.plot(fft_freq_rf, np.abs(rf_fft))
plt.title('Frequenzbereich RF-Puls')
plt.xlabel('Frequenz (Hz)')
plt.ylabel('Amplitude')

# plt.show()


# %%
# seq.write('../Test/se_rf_flip.seq', False)
# %%
