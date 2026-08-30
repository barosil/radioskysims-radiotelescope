"""Builders de componentes do pacote (composition root — strategy).
Extraído de ``radioskysims.bootstrap.builders`` na Fase 5.
Copyright BINGO Collaboration
"""

from __future__ import annotations

from pathlib import Path

from radioskysims_core.config.config_loader import build_radiotelescope_from_settings
from radioskysims_core.domain.common import FrequencyRange
from radioskysims_radiotelescope.domain.radiotelescope.specs import RadiotelescopeSpec


def build_configuration(
    telescope: str = "default",
    *,
    settings_file: str | Path | None = None,
) -> dict[str, object]:
    """Carrega configuracao concreta de radiotelescopio e derivados."""

    rt: RadiotelescopeSpec = build_radiotelescope_from_settings(
        telescope, settings_file=settings_file
    )

    observer = rt.observer
    antenna = rt.antennas[0]
    backend = antenna.backend

    time_range = observer.timeframe

    frequency_range: FrequencyRange | None = None

    if backend is not None and backend.frequency_range is not None:
        frequency_range = backend.frequency_range

    elif antenna.frequency_range is not None:
        frequency_range = antenna.frequency_range

    if frequency_range is None:
        msg = "settings.toml deve definir um frequency_range no backend ou na antena"
        raise ValueError(msg)

    return {
        "telescope_name": telescope,
        "observer": observer,
        "time_range": time_range,
        "frequency_range": frequency_range,
        "antenna": antenna,
    }
