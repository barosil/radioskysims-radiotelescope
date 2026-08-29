from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from radioskysims_core.domain.common import FrequencyRange
from radioskysims_radiotelescope.domain.radiotelescope.backend.spectrometer.models import (
    SpectrometerBackend,
)


class Pointing(BaseModel):
    """Pointing configuration for a transit telescope (alt/az)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    mode: str = Field(default="transit")
    alt_deg: float = Field(default=90.0, description="Altitude in degrees")
    az_deg: float = Field(default=0.0, description="Azimuth in degrees")
    params: dict[str, float | int | str] = Field(default_factory=dict)


class BeamSpec(BaseModel):
    """Lightweight beam description for configuration wiring.

    Supports both file-based (``beam_pattern_file``) and analytical
    (``profile`` + ``beam_width_deg``) beams.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str | None = None
    polarizations: list[str] = Field(default_factory=list)
    beam_pattern_file: str | None = None
    frequency_range: FrequencyRange | None = None
    profile: str | None = Field(
        default=None,
        description='Analytical profile: "gaussian", "airy", etc.',
    )
    beam_width_deg: float | None = Field(
        default=None,
        description="Beam width in degrees (sigma for gaussian).",
    )


class Antenna(BaseModel):
    """Physical and observational configuration of an antenna.

    ``effective_area_m2`` is the effective collecting area used for the
    absolute radiometric conversion of discrete-source flux density into
    antenna temperature.

    It is intentionally independent of the normalized angular beam response:
    the beam describes the relative response as a function of direction,
    while ``effective_area_m2`` sets the absolute collecting scale.

    The field remains optional for backwards compatibility and for workflows
    that operate directly on sky-temperature maps. Discrete-source absolute
    radiometry must provide it explicitly.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str

    effective_area_m2: float | None = Field(
        default=None,
        gt=0.0,
        description="Effective collecting area of the antenna in square metres.",
    )

    frequency_range: FrequencyRange | None = None
    pointing: Pointing = Field(default_factory=Pointing)
    beam: BeamSpec | None = None
    backend: SpectrometerBackend | None = None
