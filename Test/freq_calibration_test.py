# %%
from math import pi
import pypulseq as pp
import numpy as np

# %%
# Define system
system = pp.Opts(
    rf_dead_time=20e-6,        # time delay at the end of RF event
)
seq = pp.Sequence(system)

# Parameters
rf_duration = 200e-6
num_samples = 5000
adc_duration = 3e-3 # 3 / 4 ms
te = 20e-3

# 90 degree
rf_90 = pp.make_block_pulse(
    flip_angle=pi/2,              
    duration=rf_duration,     
    system=system,
)

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

delay_1 = pp.make_delay(te / 2 - pp.calc_duration(rf_90) / 2 - pp.calc_duration(rf_180) / 2)
delay_2 = pp.make_delay(te / 2 - pp.calc_duration(rf_180) / 2 - adc_duration / 2)
    

seq.add_block(rf_90)
seq.add_block(delay_1)
seq.add_block(rf_180)
seq.add_block(delay_2)
seq.add_block(adc)

# %%
seq.plot()

# %%
# seq.write('../Test/se_rf_flip.seq', False)
# %%
