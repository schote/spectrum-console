"""Interface class for acquisition parameters."""

from dataclasses import dataclass, asdict


@dataclass(slots=True, frozen=True)
class Dimensions:
    """Dataclass for definition of dimensional parameters."""

    x: float | int  # pylint: disable=invalid-name
    y: float | int  # pylint: disable=invalid-name
    z: float | int  # pylint: disable=invalid-name


@dataclass(slots=True, frozen=True)
class AcquisitionParameter:
    """Parameters which define an acquisition."""

    larmor_frequency: float
    b1_scaling: float
    fov_offset: Dimensions
    fov_scaling: Dimensions
    adc_samples: int
    downsampling_rate: int = 200
    num_averages: int = 1
    
    def dict(self, use_strings: bool = False) -> dict:
        """Return acquisition parameters as dictionary.

        Parameters
        ----------
        use_strings, optional
            boolean flag indicating if values of dictionary should be represented as strings, by default False

        Returns
        -------
            Acquisition parameter dictionary
        """
        if use_strings:
            return {k: str(v) for k, v in asdict(self).items()}
        else:
            return asdict(self)