# packages/radioskysims-radiotelescope/src/radioskysims_radiotelescope/application/radiotelescope_panel.py
import panel as pn
from radioskysims_viz import PanelApplication

from radioskysims_radiotelescope.domain.radiotelescope.factory import RadiotelescopeFactory


class RadiotelescopePanel(PanelApplication):
    def __init__(self, beams: list[tuple[int, str]], **kwargs):
        self.beams = beams
        super().__init__(**kwargs)

    def build_sidebar(self):
        # Widgets
        self.lat_input = pn.widgets.FloatInput(name="Latitude", step=0.0001, value=0.0)
        self.lon_input = pn.widgets.FloatInput(name="Longitude", step=0.0001, value=0.0)
        self.alt_input = pn.widgets.FloatInput(name="Altitude (m)", step=1, value=0.0)

        self.freq_range_slider = pn.widgets.RangeSlider(
            name="Faixa de Frequência (Hz)", start=1e6, end=10e9, step=1e6, value=(1.4e9, 1.6e9)
        )

        self.beam_selector = pn.widgets.Select(
            name="Beam", options={name: bid for bid, name in self.beams}
        )

        self.create_button = pn.widgets.Button(name="Criar Radiotelescópio", button_type="primary")

        # Callback
        self.create_button.on_click(self._create_radiotelescope)

        return pn.Column(
            self.lat_input,
            self.lon_input,
            self.alt_input,
            self.freq_range_slider,
            self.beam_selector,
            self.create_button,
        )

    def build_main(self):
        self.output = pn.pane.Str("")
        return pn.Column("# 🔭 Radiotelescope Configurator", self.output)

    def _create_radiotelescope(self, event=None):
        freq_min, freq_max = self.freq_range_slider.value
        beam_id = self.beam_selector.value

        telescope = RadiotelescopeFactory.create(
            lat=self.lat_input.value,
            lon=self.lon_input.value,
            alt=self.alt_input.value,
            freq_min=freq_min,
            freq_max=freq_max,
            beam_id=beam_id,
        )

        self.output.object = f"✅ Radiotelescope criado: {telescope}"

    def panel(self):
        """Compat: retorna o layout renderizável (herdado de PanelApplication)."""
        return self.__panel__()


# Para rodar standalone: python -m radioskysims_radiotelescope.application.radiotelescope_panel
if __name__ == "__main__":
    beams = [(1, "Beam Gaussiano"), (2, "Beam Real")]
    RadiotelescopePanel(beams).serve(show=True)
