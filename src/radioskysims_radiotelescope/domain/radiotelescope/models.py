"""Modelos de radiotelescópio (persistência)."""

from __future__ import annotations

from sqlmodel import Field, SQLModel


class Radiotelescope(SQLModel, table=True):
    __tablename__ = "radiotelescopes"

    id: int | None = Field(default=None, primary_key=True)

    # Exemplo: latitude, longitude, altitude
    earth_location_lat: float
    earth_location_lon: float
    earth_location_alt: float

    # Faixa de frequência em Hz
    frequency_min: float
    frequency_max: float

    # Referência ao Beam (inteiro simples; sem FK — não existe tabela "beams")
    beam_id: int | None = Field(default=None)

    @property
    def frequency_range(self) -> tuple[float, float]:
        return (self.frequency_min, self.frequency_max)

    def __repr__(self) -> str:
        return (
            f"<Radiotelescope(loc=({self.earth_location_lat}, {self.earth_location_lon}), "
            f"freq_range={self.frequency_range}, beam_id={self.beam_id})>"
        )
