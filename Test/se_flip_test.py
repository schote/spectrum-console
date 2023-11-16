# %%
from math import pi
import pypulseq as pp
import numpy as np

# %%
# Define system
system = pp.Opts(
    rf_ringdown_time=100e-6,    # Time delay at the beginning of an RF event
    rf_dead_time=100e-6,        # time delay at the end of RF event
    adc_dead_time=200e-6,       # time delay at the beginning of ADC event
)
seq = pp.Sequence(system)

# Parameters
rf_duration = 250e-6 #200
num_samples = 5000
adc_duration = 3e-3 # 3 / 4 ms
te = 20e-3

# 180 degree
rf_180 = pp.make_block_pulse(
    flip_angle=pi,              
    duration=rf_duration*2,     
    system=system,
)

# ADC event
adc = pp.make_adc(
    num_samples=num_samples,
    duration=adc_duration, 
    system=system
)

delay_2 = pp.make_delay(te / 2 - pp.calc_duration(rf_180) / 2 - adc_duration / 2)

flip_step = 5  
min_flip_angle = 65
max_flip_angle = 80

# rf_flip = None 
# Updating current flip angle
for rf_flip_deg in range(min_flip_angle, max_flip_angle + 1, flip_step):
    rf_flip = rf_flip_deg * np.pi / 180
    rf1 = pp.make_block_pulse(
        rf_flip,
        duration=rf_duration,
        system=system
    )
    
    delay_1 = pp.make_delay(te / 2 - 
        pp.calc_duration(rf1) / 2 -
        pp.calc_duration(rf_180) / 2)
    

    seq.add_block(rf1)
    seq.add_block(delay_1)
    seq.add_block(rf_180)
    seq.add_block(delay_2)
    seq.add_block(adc)
    seq.add_block(pp.make_delay(8e-3)) # Delay (TR?) bis nächster Puls startet


# %%
print('Delay1' ,delay_1)
print('Delay2' , delay_2)

# %%
seq.plot()

# %%
# seq.write('../Test/se_rf_flip.seq', False)
# %%
