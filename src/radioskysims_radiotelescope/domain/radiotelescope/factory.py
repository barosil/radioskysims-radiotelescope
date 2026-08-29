# src/radioskysims/domain/radiotelescope/factory.py
from __future__ import annotations

from radioskysims_radiotelescope.domain.radiotelescope.models import Radiotelescope


class RadiotelescopeFactory:
    @staticmethod
    def create(
        lat: float,
        lon: float,
        alt: float,
        freq_min: float,
        freq_max: float,
        beam_id: int | None = None,
    ) -> Radiotelescope:
        """Cria um objeto Radiotelescope a partir dos parâmetros fornecidos."""
        return Radiotelescope(
            earth_location_lat=lat,
            earth_location_lon=lon,
            earth_location_alt=alt,
            frequency_min=freq_min,
            frequency_max=freq_max,
            beam_id=beam_id,
        )
