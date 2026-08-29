from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from radioskysims_core.domain.common import FrequencyRange


class SpectrometerBackend(BaseModel):
    """Spectrometer backend configuration (single backend for now)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    kind: str = "spectrometer"
    name: str | None = None
    bandwidth_mhz: float | None = None
    sampling_rate_mhz: float | None = None
    integration_time_s: float | None = None
    num_channels: int | None = None
    system_temperature_k: float | None = None
    frequency_range: FrequencyRange | None = None

    def as_dict(self) -> dict:
        return self.model_dump(exclude_none=True)
