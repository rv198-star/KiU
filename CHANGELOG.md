# Changelog

## Unreleased

### Added
- `llm-assisted` drafting now performs real `Rationale` generation with prompt templates, provider abstraction, validator precheck, rejection logging, and token-budget tracking.
- `reports/rounds/*.json` now records auditable LLM prompt/response artifacts for drafting rounds.

### Changed
- Renamed scheduler config from `autonomous_refiner` to `refinement_scheduler`.
- Kept backward-compatible YAML alias loading for legacy `autonomous_refiner` bundles, with a deprecation warning during profile resolution.
