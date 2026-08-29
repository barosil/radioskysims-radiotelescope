# radioskysims-radiotelescope

Radiotelescópio do ecossistema **RadioSkySim**.

## Conteúdo

- `domain.radiotelescope` — `Radiotelescope`, `RadiotelescopeFactory`,
  antena, backend/spectrometer, specs
- `application.radiotelescope_panel` — `RadiotelescopePanel`
  (subclasse de `PanelApplication`)
- `application.services.radiotelescope_services`

## Dependências

`numpy`, `pydantic`, `panel`, `radioskysims-core`, `radioskysims-viz`.

## Testes

```bash
uv run --package radioskysims-radiotelescope pytest
```
