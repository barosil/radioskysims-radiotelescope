from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from radioskysims_core.domain.common import Observer
from radioskysims_radiotelescope.domain.radiotelescope.antenna.models import Antenna


class RadiotelescopeSpec(BaseModel):
    """Domain specification for a radiotelescope setup.

    A radiotelescope has a geographic position (observer) and one or more
    antennas, each with its own backend (e.g. spectrometer).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    observer: Observer
    antennas: list[Antenna]
