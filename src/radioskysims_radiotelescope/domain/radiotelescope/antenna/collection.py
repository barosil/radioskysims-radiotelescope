"""\
Módulo: src/radioskysims_radiotelescope/domain/radiotelescope/antenna/collection.py

Descrição:
    Container de antenas de um radiotelescópio. Encapsula a lista de
    ``Antenna`` preservando o comportamento de sequência (indexação,
    iteração, tamanho) e expõe propriedades derivadas de forma
    explorável (``get_properties``), com ``__repr__`` que lista as
    propriedades disponíveis.

Copyright BINGO Collaboration
Last modified: 2026-08-30
"""

from __future__ import annotations

from typing import Any, Iterator

from pydantic import BaseModel, ConfigDict, Field

from radioskysims_radiotelescope.domain.radiotelescope.antenna.models import Antenna

# Registro de propriedades derivadas: nome canônico -> (atributo, unidade, plot).
# ``attr=None`` indica propriedade especial (não é atributo escalar da Antenna).
# ``plot`` indica o builder holoviews usado por ``AntennaPropertyView.view()``.
_PROPERTY_REGISTRY: dict[str, tuple[str | None, str | None, str]] = {
    "FWHM": ("fwhm_deg", "deg", "fwhm"),
    "Gain": ("gain_dbi", "dBi", "gain"),
    "BeamPattern": (None, None, "beam_pattern"),
    "effective_area": ("effective_area_m2", "m²", "table"),
    "beam_width": ("beam_width_deg", "deg", "table"),
    "frequency_range": ("frequency_range", "MHz", "table"),
    "num_channels": ("num_channels", None, "table"),
    "bandwidth": ("bandwidth_mhz", "MHz", "table"),
    "system_temperature": ("system_temperature_k", "K", "table"),
}


def _normalize_property_name(name: str) -> str:
    """Normaliza um nome de propriedade (case-insensitive, sem espaços/_ ).

    Ex.: ``"fwhm"``, ``"FWHM"`` e ``" fwhm "`` mapeiam para ``"FWHM"``;
    ``"beampattern"``/``"beam_pattern"`` mapeiam para ``"BeamPattern"``.
    """
    original = name.strip().lower()
    compact = original.replace("_", "").replace(" ", "")
    for canonical in _PROPERTY_REGISTRY:
        canonical_compact = canonical.lower().replace("_", "").replace(" ", "")
        if compact == canonical_compact:
            return canonical
    return original


class AntennaPropertyView:
    """Visão de uma propriedade derivada, avaliada para cada antena.

    É o resultado de ``Antennas.get_properties(name)``. ``view()`` devolve
    uma visualização interativa holoviews (gráfico para FWHM/Gain/
    BeamPattern, tabela para as demais); ``summary()``/``repr`` devolvem
    uma tabela textual antena → valor.
    """

    def __init__(
        self,
        name: str,
        values: dict[str, Any],
        unit: str | None = None,
        *,
        plot_kind: str = "table",
        antennas: Antennas | None = None,
    ) -> None:
        self.name = name
        self.values = values  # nome da antena -> valor da propriedade
        self.unit = unit
        self._plot_kind = plot_kind
        self._antennas = antennas

    def __repr__(self) -> str:
        return self.summary()

    def __len__(self) -> int:
        return len(self.values)

    def summary(self) -> str:
        """Tabela textual antena → valor (usada por ``repr``)."""
        header = f"Property: {self.name}"
        if self.unit:
            header += f" ({self.unit})"
        lines = [header]
        for ant_name, value in self.values.items():
            if isinstance(value, float):
                lines.append(f"  {ant_name}: {value:.4g}")
            else:
                lines.append(f"  {ant_name}: {value}")
        return "\n".join(lines)

    def view(self):
        """Retorna a visão interativa (holoviews) da propriedade.

        - ``FWHM`` → curva FWHM × frequência;
        - ``Gain`` → curva Ganho (dBi) × frequência;
        - ``BeamPattern`` → padrão de feixe (dB) × ângulo para 5
          frequências espaçadas na faixa;
        - demais → tabela holoviews antena → valor.

        O import de ``radioskysims-viz`` é lazy (renderização fica na
        camada de visualização).
        """
        from radioskysims_viz.radiotelescope import (
            beam_pattern_plot,
            fwhm_plot,
            gain_plot,
            property_table,
        )

        if self._plot_kind == "fwhm":
            return fwhm_plot(self._antennas)
        if self._plot_kind == "gain":
            return gain_plot(self._antennas)
        if self._plot_kind == "beam_pattern":
            return beam_pattern_plot(self._antennas)
        return property_table(self.name, self.values, self.unit)


class Antennas(BaseModel):
    """Coleção de antenas de um radiotelescópio.

    Mantém compatibilidade com sequência (``antennas[0]``, ``len``,
    iteração e ``list(antennas)``) e adiciona exploração de propriedades
    derivadas via :meth:`get_properties`.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    antennas: list[Antenna] = Field(default_factory=list)

    # ── Protocolo de sequência ───────────────────────────────────────
    def __getitem__(self, index: int | slice) -> Antenna | list[Antenna]:
        return self.antennas[index]

    def __iter__(self) -> Iterator[Antenna]:
        return iter(self.antennas)

    def __len__(self) -> int:
        return len(self.antennas)

    def __contains__(self, item: object) -> bool:
        return item in self.antennas

    # ── Introspecção ─────────────────────────────────────────────────
    @property
    def names(self) -> list[str]:
        """Nomes das antenas na ordem da configuração."""
        return [a.name for a in self.antennas]

    @classmethod
    def available_properties(cls) -> list[str]:
        """Propriedades derivadas disponíveis para consulta."""
        return list(_PROPERTY_REGISTRY)

    def __repr__(self) -> str:
        names = ", ".join(repr(a.name) for a in self.antennas)
        props = ", ".join(self.available_properties())
        return (
            f"Antennas(n={len(self.antennas)}, names=[{names}])\n"
            f"Available properties: {props}"
        )

    def __str__(self) -> str:
        # pydantic v2 define __str__ separadamente; delega para o __repr__
        # customizado para manter a mesma saída em print()/repr().
        return self.__repr__()

    # ── Propriedades derivadas ───────────────────────────────────────
    def get_properties(self, name: str) -> AntennaPropertyView:
        """Avalia uma propriedade (ex.: ``"FWHM"``, ``"Gain"``) por antena.

        Propriedades conhecidas (ver :meth:`available_properties`) são
        resolvidas por unidade. Nomes desconhecidos são tratados como
        atributos brutos da ``Antenna`` (ex.: ``"name"``).

        Args:
            name: Nome da propriedade (case-insensitive).

        Returns:
            :class:`AntennaPropertyView` com valor por antena e unidade.

        Raises:
            AttributeError: Se ``name`` não for uma propriedade conhecida
                nem um atributo da ``Antenna``.
        """
        canonical = _normalize_property_name(name)
        if canonical in _PROPERTY_REGISTRY:
            attr, unit, plot_kind = _PROPERTY_REGISTRY[canonical]
            display_name = canonical
        else:
            attr, unit, plot_kind = canonical, None, "table"
            display_name = name

        values: dict[str, Any] = {}
        for antenna in self.antennas:
            if attr is None:
                # Propriedade especial (ex.: BeamPattern) — guarda a antena.
                values[antenna.name] = antenna
                continue
            # Resolve o atributo na Antenna; se não existir, tenta o backend.
            value: Any
            try:
                value = getattr(antenna, attr)
            except AttributeError:
                if antenna.backend is not None:
                    value = getattr(antenna.backend, attr)
                else:
                    raise
            values[antenna.name] = value
        return AntennaPropertyView(
            display_name,
            values,
            unit,
            plot_kind=plot_kind,
            antennas=self,
        )
