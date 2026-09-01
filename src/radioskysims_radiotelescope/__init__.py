"""
Pacote: radioskysims_radiotelescope

Radiotelescópio do ecossistema RadioSkySim — domínio (pointing, antena,
backend/spectrometer), factory/specs e painel de visualização
(PanelApplication).

Copyright BINGO Collaboration
"""

from __future__ import annotations

__version__ = "0.1.0"

from .domain.radiotelescope import (
    AntennaPropertyView,
    Antennas,
    Radiotelescope,
    RadiotelescopeFactory,
    RadiotelescopeSpec,
)

__all__ = [
    "AntennaPropertyView",
    "Antennas",
    "Radiotelescope",
    "RadiotelescopeFactory",
    "RadiotelescopeSpec",
]
