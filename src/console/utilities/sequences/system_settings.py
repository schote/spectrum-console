"""Global definition of system settings to be imported by sequence constructors."""
from pypulseq.opts import Opts

system = Opts(
    # time delay at the end of RF event, SETS RF DELAY!
    rf_dead_time=20e-6,

    # Set raster times to spectrum card frequency (timing checks)
    grad_raster_time=1e-6,
    rf_raster_time=1e-6,
    block_duration_raster=1e-6,
    adc_raster_time=1e-6,

    # Time delay at the beginning of an RF event
    # rf_ringdown_time=100e-6,
    # Time delay at the beginning of ADC event
    # adc_dead_time=200e-6,

    # Set maximum slew rate
    max_slew=5000,
    slew_unit="T/m/s",
)
