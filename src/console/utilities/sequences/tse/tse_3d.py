"""Constructor for 3D TSE Imaging sequence."""
# %%
from math import pi

import numpy as np
import pypulseq as pp

from console.interfaces.interface_dimensions import Dimensions
from console.utilities.sequences.system_settings import raster, system

default_fov = Dimensions(x=220e-3, y=220e-3, z=225e-3)
default_encoding = Dimensions(x=70, y=70, z=49)


def constructor(
    echo_time: float = 15e-3,
    repetition_time: float = 600e-3,
    etl: int = 7,
    rf_duration: float = 400e-6,
    ramp_duration:float = 200e-6,
    gradient_correction: float = 0.,
    adc_correction: float = 0.,
    ro_bandwidth: float = 20e3,
    fov: Dimensions = default_fov,
    n_enc: Dimensions = default_encoding,
) -> tuple[pp.Sequence, list]:
    """Construct 3D turbo spin echo sequence.

    Parameters
    ----------
    echo_time, optional
        Time constant between center of 90 degree pulse and center of ADC, by default 15e-3
    repetition_time, optional
        Time constant between two subsequent 90 degree pulses (echo trains), by default 600e-3
    etl, optional
        Echo train length, by default 7
    rf_duration, optional
        Duration of the RF pulses (90 and 180 degree), by default 400e-6
    gradient_correction, optional
        Time constant to center ADC event, by default 510e-6
    adc_correction, optional
        Time constant which is added at the end of the ADC and readout gradient.
        This value is not taken into account for the prephaser calculation.
    ro_bandwidth, optional
        Readout bandwidth in Hz, by default 20e3
    fov, optional
        Field of view per dimension, by default default_fov
    n_enc, optional
        Number of encoding steps per dimension, by default default_encoding = Dimensions(x=70, y=70, z=49).
        If an encoding dimension is set to 1, the TSE sequence becomes a 2D sequence.

    Returns
    -------
        Pulseq sequence and a list which describes the trajectory
    """
    system.rf_ringdown_time = 0
    seq = pp.Sequence(system)
    seq.set_definition("Name", "tse_3d")

    # Channel assignment
    channel_ro = "y"
    channel_pe1 = "z"
    channel_pe2 = "x"

    # Definition of RF pulses
    rf_90 = pp.make_block_pulse(system=system, flip_angle=pi / 2, phase_offset = 0, duration=rf_duration, use="excitation")
    rf_180 = pp.make_block_pulse(system=system, flip_angle=pi,phase_offset =pi/2,duration=rf_duration, use="refocusing")

    # ADC duration
    adc_duration = n_enc.x / ro_bandwidth

    # Define readout gradient and prewinder
    grad_ro = pp.make_trapezoid(
        channel=channel_ro,
        system=system,
        flat_area=n_enc.x / fov.x,
        rise_time=ramp_duration,
        fall_time=ramp_duration,
        # Add gradient correction time and ADC correction time
        flat_time=raster(adc_duration, precision=system.grad_raster_time),
    )

    grad_ro = pp.make_trapezoid(
        channel=channel_ro,
        system=system,
        amplitude=grad_ro.amplitude,
        rise_time=ramp_duration,
        fall_time=ramp_duration,
        # Add gradient correction time and ADC correction time
        flat_time=raster(adc_duration + 2*gradient_correction + 2*adc_correction, precision=system.grad_raster_time),
    )

    # Calculate readout prephaser without correction times
    ro_pre_duration = pp.calc_duration(grad_ro) / 2

    grad_ro_pre = pp.make_trapezoid(
        channel=channel_ro,
        system=system,
        area=grad_ro.area / 2,
        rise_time=ramp_duration,
        fall_time=ramp_duration,
        duration=raster(ro_pre_duration, precision=system.grad_raster_time),
        # flat_time=raster(ro_pre_duration + gradient_correction + adc_correction, precision=system.grad_raster_time),

    )

    adc = pp.make_adc(
        system=system,
        num_samples=int((adc_duration + adc_correction)/system.adc_raster_time),
        duration=raster(val=adc_duration + adc_correction, precision=system.adc_raster_time),
        # Add gradient correction time and ADC correction time
        delay=raster(val=2*gradient_correction + grad_ro.rise_time, precision=system.adc_raster_time)
    )

    # Calculate delays
    # Note: RF dead-time is contained in RF delay
    # Delay duration between RO prephaser after initial 90 degree RF and 180 degree RF pulse
    tau_1 = echo_time / 2 - rf_duration - rf_90.ringdown_time - rf_180.delay - ro_pre_duration
    # Delay duration between Gy, Gz prephaser and readout
#    tau_2 = (echo_time - rf_duration - pp.calc_duration(grad_ro)) / 2 - rf_180.ringdown_time - ro_pre_duration
    tau_2 = (echo_time - rf_duration - adc_duration) / 2 - 2*gradient_correction - adc_correction - ramp_duration - rf_180.ringdown_time - ro_pre_duration
    # Delay duration between readout and Gy, Gz gradient rephaser
#    tau_3 = (echo_time - rf_duration - pp.calc_duration(grad_ro)) / 2 - rf_180.delay - ro_pre_duration
    tau_3 = (echo_time - rf_duration - adc_duration) / 2 - ramp_duration - adc_correction - rf_180.delay - ro_pre_duration
    # Delay between echo trains
    tr_delay = repetition_time - echo_time - adc_duration / 2 - rf_90.delay

    # Calculate center out trajectory
    pe0 = np.arange(n_enc.y) - (n_enc.y - 1) / 2
    pe1 = np.arange(n_enc.z) - (n_enc.z - 1) / 2

    # Add offset of -0.1 to ensure that positive PE step comes first:
    # e.g. PE values without offset (-1, 0, 1) -> abs: (1, 0, 1) -> argsort: (1, 0/2)
    # PE values with offset (-1.1, -0.1, 0.9) -> abs: (1.1, 0.1, 0.9) -> argsort: (1, 2, 0)
    pe0_ordered = pe0[np.argsort(np.abs(pe0 - 0.1))]
    pe1_ordered = pe1[np.argsort(np.abs(pe1 - 0.1))]

    pe_traj = np.stack([grid.flatten() for grid in np.meshgrid(pe0_ordered, pe1_ordered, indexing='ij')], axis=-1)

    pe_traj[:, 0] /= fov.y
    pe_traj[:, 1] /= fov.z

    # Divide all PE steps into echo trains
    num_trains = int(np.ceil(pe_traj.shape[0] / etl))
    trains = [pe_traj[k*etl:(k+1)*etl] for k in range(num_trains)]

    ro_counter = 0

    for train in trains:

        seq.add_block(rf_90)
        seq.add_block(grad_ro_pre)
        seq.add_block(pp.make_delay(raster(val=tau_1, precision=system.grad_raster_time)))

        for echo in train:

            pe_0, pe_1 = echo

            seq.add_block(rf_180)

            seq.add_block(
                pp.make_trapezoid(channel=channel_pe1, area=-pe_0, duration=ro_pre_duration, system=system, rise_time=ramp_duration, fall_time=ramp_duration),
                pp.make_trapezoid(channel=channel_pe2, area=-pe_1, duration=ro_pre_duration, system=system, rise_time=ramp_duration, fall_time=ramp_duration)
            )

            seq.add_block(pp.make_delay(raster(val=tau_2, precision=system.grad_raster_time)))

            seq.add_block(grad_ro, adc)

            seq.add_block(
                pp.make_trapezoid(channel=channel_pe1, area=pe_0, duration=ro_pre_duration, system=system, rise_time=ramp_duration, fall_time=ramp_duration),
                pp.make_trapezoid(channel=channel_pe2, area=pe_1, duration=ro_pre_duration, system=system, rise_time=ramp_duration, fall_time=ramp_duration)
            )

            seq.add_block(pp.make_delay(raster(val=tau_3, precision=system.grad_raster_time)))

            ro_counter += 1

        # Add TR after echo train, if not the last readout
        if ro_counter < n_enc.y * n_enc.z:
            seq.add_block(pp.make_delay(raster(val=tr_delay, precision=system.block_duration_raster)))

    # Calculate some sequence measures
    train_duration_tr = (seq.duration()[0] + tr_delay) / len(trains)
    train_duration = train_duration_tr - tr_delay

    # Add measures to sequence definition
    seq.set_definition("n_total_trains", len(trains))
    seq.set_definition("train_duration", train_duration)
    seq.set_definition("train_duration_tr", train_duration_tr)
    seq.set_definition("tr_delay", tr_delay)

    return (seq, pe_traj)



def sort_kspace(kspace: np.ndarray, trajectory: np.ndarray, dim: Dimensions) -> np.ndarray:
    """
    Sort acquired k-space lines.

    Parameters
    ----------
    kspace
        Acquired k-space data in the format (averages, coils, pe, ro)
    trajectory
        k-Space trajectory returned by TSE constructor with dimension (pe, 2)
    """
    # Last key in the sequence passed to lexsort is used for the primary key
    # Trajectory is passed as (y-koords, z-koords) to obtain zy-order
    # Neg. sign sorts trajectory in descending order
    order = np.lexsort((-trajectory[:, 0], -trajectory[:, 1]))
    # Apply the order to the phase encoding dimension of k-space
    ksp_sorted = kspace[..., order, :]
    n_avg, n_coil, _, n_ro = kspace.shape
    return np.reshape(ksp_sorted, (n_avg, n_coil, int(dim.z), int(dim.y), n_ro))
