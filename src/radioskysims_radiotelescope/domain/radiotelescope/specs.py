from __future__ import annotations

import astropy.units as u
from pydantic import BaseModel, ConfigDict, field_validator

from radioskysims_core.domain.common import Observer
from radioskysims_radiotelescope.domain.radiotelescope.antenna.collection import Antennas


class RadiotelescopeSpec(BaseModel):
    """Domain specification for a radiotelescope setup.

    A radiotelescope has a geographic position (observer) and one or more
    antennas, each with its own backend (e.g. spectrometer).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    observer: Observer
    antennas: Antennas

    @field_validator("antennas", mode="before")
    @classmethod
    def _coerce_antennas(cls, v: object) -> object:
        """Aceita ``list[Antenna]`` e converte para o container ``Antennas``."""
        if isinstance(v, list):
            return Antennas(antennas=v)
        return v

    def __repr__(self) -> str:
        obs = self.observer
        lat = float(obs.lat.to_value(u.deg))
        lon = float(obs.lon.to_value(u.deg))
        names = ", ".join(self.antennas.names) or "-"
        return (
            f"RadiotelescopeSpec(name={self.name!r}, antennas={len(self.antennas)} "
            f"[{names}], loc=({lat:+.4f}°, {lon:+.4f}°))"
        )

    def __str__(self) -> str:
        # pydantic v2 define __str__ separadamente; delega para o __repr__
        # customizado para manter a mesma saída em print()/repr().
        return self.__repr__()

    def view(self) -> str:
        """Visão textual completa do radiotelescópio (observador + antenas)."""
        return "\n".join(
            [
                repr(self),
                "",
                self.observer.view(),
                "",
                "Antennas:",
                repr(self.antennas),
            ]
        )
