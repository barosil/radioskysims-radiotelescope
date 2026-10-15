from __future__ import annotations

import math

from pydantic import BaseModel, ConfigDict, Field, model_validator
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

    gain_dbi: float | None = Field(
        default=None,
        description=(
            "Ganho direcional (dBi). Populado na montagem do conjunto de "
            "informações quando não informado explicitamente."
        ),
    )

    # ── Propriedades físicas derivadas ────────────────────────────────
    # Fator de conversão sigma→FWHM para perfil gaussiano:
    #   FWHM = 2 * sqrt(2 * ln(2)) * sigma ≈ 2.35482 * sigma
    _GAUSSIAN_FWHM_FACTOR: float = 2.0 * math.sqrt(2.0 * math.log(2.0))

    @property
    def fwhm_deg(self) -> float | None:
        """Largura a meia altura (FWHM) do feixe em graus.

        Para perfil gaussiano, ``beam_width_deg`` é interpretado como
        ``sigma`` e convertido via ``FWHM = 2*sqrt(2*ln(2))*sigma``.
        Para os demais perfis, ``beam_width_deg`` é usado diretamente.
        Retorna ``None`` quando o feixe não define largura.
        """
        if self.beam is None or self.beam.beam_width_deg is None:
            return None
        width_deg = self.beam.beam_width_deg
        profile = (self.beam.profile or "").strip().lower()
        if profile == "gaussian":
            return width_deg * self._GAUSSIAN_FWHM_FACTOR
        return width_deg

    @model_validator(mode="after")
    def _populate_gain_dbi(self) -> Antenna:
        """Popula ``gain_dbi`` na montagem quando não informado (None)."""
        if self.gain_dbi is None:
            self.gain_dbi = self._estimate_gain_dbi()
        return self

    def _estimate_gain_dbi(self) -> float | None:
        """Estimativa de ganho (dBi) a partir da área efetiva ou do FWHM.

        Prioriza ``G = 4π A_eff / λ²`` (frequência central); sem área efetiva,
        estima pelo ângulo sólido gaussiano do feixe (``Ω ≈ 1.133·θ²``) e
        ``G ≈ 4π / Ω``. Retorna ``None`` sem dados suficientes.
        """
        if self.effective_area_m2 is not None and self.frequency_range is not None:
            fc_mhz = (self.frequency_range.min_mhz + self.frequency_range.max_mhz) / 2.0
            lam_m = 299_792_458.0 / (fc_mhz * 1e6)  # c / f (metros)
            gain = 4.0 * math.pi * self.effective_area_m2 / (lam_m * lam_m)
            if gain > 0.0:
                return 10.0 * math.log10(gain)

        fwhm_deg = self.fwhm_deg
        if fwhm_deg is None or fwhm_deg <= 0.0:
            return None
        theta_rad = math.radians(fwhm_deg)
        solid_angle_sr = 1.133 * theta_rad * theta_rad
        gain = 4.0 * math.pi / solid_angle_sr
        return 10.0 * math.log10(gain)
