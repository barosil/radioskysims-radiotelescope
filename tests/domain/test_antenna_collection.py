"""\
Módulo: tests/domain/test_antenna_collection.py

Descrição:
    Testes do container ``Antennas`` e das propriedades derivadas de
    ``Antenna`` (FWHM/Gain) implementadas para a célula 2 do notebook
    de exemplos.

Copyright BINGO Collaboration
Last modified: 2026-08-30
"""

from __future__ import annotations

import pytest

from radioskysims_core.domain.common import FrequencyRange
from radioskysims_radiotelescope.domain.radiotelescope.antenna import (
    Antenna,
    Antennas,
    BeamSpec,
)


def _make_antenna(
    name: str = "horn",
    beam_width_deg: float | None = 15.0,
    profile: str | None = None,
    effective_area_m2: float | None = None,
) -> Antenna:
    return Antenna(
        name=name,
        effective_area_m2=effective_area_m2,
        frequency_range=FrequencyRange(min_mhz=1000.0, max_mhz=1250.0, resolution_mhz=0.05),
        beam=BeamSpec(name="beam", beam_width_deg=beam_width_deg, profile=profile),
    )


class TestAntennasContainer:
    def test_sequence_protocol(self) -> None:
        antennas = Antennas(antennas=[_make_antenna("a"), _make_antenna("b")])
        assert len(antennas) == 2
        assert antennas[0].name == "a"
        assert antennas[1].name == "b"
        assert [a.name for a in antennas] == ["a", "b"]
        assert list(antennas)[0].name == "a"
        assert "a" not in antennas  # contém objetos Antenna, não nomes

    def test_repr_lists_available_properties(self) -> None:
        antennas = Antennas(antennas=[_make_antenna("horn")])
        text = repr(antennas)
        assert "Antennas(n=1" in text
        assert "horn" in text
        assert "Available properties:" in text
        assert "FWHM" in text
        assert "Gain" in text

    def test_str_matches_repr(self) -> None:
        antennas = Antennas(antennas=[_make_antenna("horn")])
        assert str(antennas) == repr(antennas)


class TestGetProperties:
    def test_fwhm_default(self) -> None:
        antennas = Antennas(antennas=[_make_antenna("horn", beam_width_deg=15.0)])
        view = antennas.get_properties("FWHM")
        assert view.values["horn"] == pytest.approx(15.0)

    def test_fwhm_gaussian_scales_sigma(self) -> None:
        antennas = Antennas(
            antennas=[_make_antenna("horn", beam_width_deg=1.0, profile="gaussian")]
        )
        view = antennas.get_properties("FWHM")
        # FWHM = 2 * sqrt(2*ln2) * sigma ≈ 2.35482
        assert view.values["horn"] == pytest.approx(2.35482, rel=1e-3)

    def test_gain_from_fwhm(self) -> None:
        antennas = Antennas(antennas=[_make_antenna("horn", beam_width_deg=15.0)])
        view = antennas.get_properties("Gain")
        gain_dbi = view.values["horn"]
        assert gain_dbi is not None
        assert gain_dbi == pytest.approx(22.09, rel=1e-2)

    def test_gain_prefers_effective_area(self) -> None:
        # A = pi*(1m)^2 -> G ~ (pi / lam^2); fc = 1125 MHz -> lam ~ 0.2665 m
        antennas = Antennas(antennas=[_make_antenna("horn", effective_area_m2=0.1)])
        view = antennas.get_properties("Gain")
        gain_dbi = view.values["horn"]
        assert gain_dbi is not None
        # 10*log10(4*pi*0.1 / lam**2)
        import math

        fc_mhz = 1125.0
        lam = 299_792_458.0 / (fc_mhz * 1e6)
        expected = 10 * math.log10(4 * math.pi * 0.1 / (lam * lam))
        assert gain_dbi == pytest.approx(expected, rel=1e-3)

    def test_unknown_property_raises(self) -> None:
        antennas = Antennas(antennas=[_make_antenna("horn")])
        with pytest.raises(AttributeError):
            antennas.get_properties("does_not_exist")

    def test_summary_renders_table(self) -> None:
        antennas = Antennas(antennas=[_make_antenna("horn", beam_width_deg=15.0)])
        text = antennas.get_properties("FWHM").summary()
        assert "Property: FWHM" in text
        assert "deg" in text
        assert "horn" in text

    def test_view_returns_holoviews_curve(self) -> None:
        antennas = Antennas(antennas=[_make_antenna("horn", beam_width_deg=15.0)])
        hv = pytest.importorskip("holoviews")
        plot = antennas.get_properties("FWHM").view()
        assert isinstance(plot, hv.Overlay)
        assert len(plot) == 1  # uma curva por antena

    def test_view_beam_pattern_five_curves(self) -> None:
        antennas = Antennas(
            antennas=[_make_antenna("horn", beam_width_deg=15.0, profile="gaussian")]
        )
        hv = pytest.importorskip("holoviews")
        plot = antennas.get_properties("BeamPattern").view()
        assert isinstance(plot, hv.Overlay)
        # 5 frequências espaçadas na faixa (perfil analítico gaussiano)
        assert len(plot) == 5
