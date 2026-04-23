# Changelog

## Unreleased

### Planned For 0.5.1
- Correct the version narrative so `0.5.0` remains the foundation closure while `0.5.1` becomes the explicit `cangjie-skill` gap-closure patch.
- Harden the same-source benchmark release gate so artifact lead alone is insufficient; `0.5.1` must show slight but explicit same-scenario superiority: positive usage delta, `usage_winner = kiu`, weighted pass-rate parity-or-better, and no boundary drift.
- Archive a fresh Poor Charlie scorecard that records benchmark paths, usage deltas, and workflow-boundary preservation evidence for the `0.5.1` release decision.

## [0.5.0] - 2026-04-22

### Added
- Added the second public domain profile `engineering` plus the reference source bundle `engineering-postmortem-v0.1`, including `postmortem-blameless`, `blast-radius-check`, and shared canonical traces/evaluation cases.
- Added cross-bundle graph merge support with `src/kiu_graph/merge.py`, `scripts/merge_graphs.py`, and validator `--merge-with` coverage for external relations.
- Added generated-run three-layer review scoring via `scripts/review_generated_run.py`, emitting `reports/three-layer-review.json` with auditable 100-point scores for source bundle, generated bundle, and usage outputs.
- Added minimum workflow deliverable skeletons for downgraded workflow candidates: `workflow.yaml` and `CHECKLIST.md` now ship under `workflow_candidates/<id>/`.

### Changed
- Hardened the workflow-vs-agentic boundary so `high/high` routing stays outside `bundle/skills/` while still preserving usable workflow preflight artifacts for audit and execution prep.
- `generate_candidates.py` and `build_candidates.py` now report workflow candidate counts from generated run metrics instead of silently under-reporting them in CLI summaries.
- Bundle validation now understands merged external bundle references and enforces the engineering-domain release path with the same structural rigor as investing.
- The v0.5 foundation line is now release-framed as: multi-domain validation, cross-bundle graph proof, explicit workflow/agentic boundary, and fresh three-layer review evidence.

## [0.4.2] - 2026-04-22

### Added
- `docs/kiu-skill-spec-v0.4.md` documents the v0.4 public surface: single-domain production-line hardening, workflow-vs-agentic routing, production quality gating, example fixtures, and honest rendered summaries.
- `docs/2026-04-22-v0.4.1-assessment-and-v0.4.2-plan.md` records the combined external review, local real-use findings, and the v0.4.2 / v0.5 split.

### Changed
- Generated candidate `SKILL.md` files now render `Evaluation Summary` from `eval/summary.yaml` and `Revision Summary` from `iterations/revisions.yaml`; refinement mutations refresh those sections instead of only bumping metadata.
- Generated-bundle preflight now rejects `Evaluation Summary` / `Revision Summary` drift against their structured YAML sources.
- `automation.yaml` profile resolution now accepts `inherits_from` as the preferred field while keeping `inherits` as a compatibility alias.
- The financial-statement example fixture now routes story-only valuation cases into `lock-onto-accounting-value` instead of excluding the exact adversarial pattern it should catch.
- Published investing skill revision notes now label the v0.4 content rewrite as a manual content upgrade rather than implying a loop-driven refinement run.

## [0.4.1] - 2026-04-22

### Added
- Example-fixture source bundles can now be scaffolded from repo fixture YAML plus compact source docs without writing generated artifacts back into the repository.
- Fixed local artifact roots under `/tmp/kiu-local-artifacts/` became the default output surface for generated bundles and scaffolded fixture sources.

### Changed
- Fixture packaging and local-output handling were hardened so v0.4 smoke bundles can be generated, inspected, and discarded without polluting git state.

## [0.4.0] - 2026-04-22

### Added
- Five published investing skills were rewritten to the v0.4 content standard with denser rationale, explicit three-trace evidence summaries, richer relation links, and revision `4`.
- Canonical trace coverage for the reference investing bundle expanded from `3` traces to `15`.
- Production quality gating now scores generated bundles with `artifact_quality`, `production_quality`, and a bundle-level grade driven by domain profile thresholds.
- Example fixtures for `effective-requirements-analysis` and `financial-statement-analysis` were added as second-line source-bundle smoke tests.

### Changed
- Reference-skill evaluation summaries now bind to full shared-corpus coverage while keeping representative case references.
- Generated candidate runs now emit release-quality reports instead of only structural bundle artifacts.

## [0.3.1] - 2026-04-22

### Added
- Published-skill density can now be enforced as a hard domain gate through profile-driven `content_density.published_requirement`.
- Validator errors now expose empty or missing shared-corpus glob expansion in generated and published evaluation bindings.

### Changed
- `_resolve_subset_cases` now expands glob case references before counting totals, rejects zero-match globs, and enforces exact `total == len(resolved_cases)` consistency.
- Investing-domain published bundles now require hard density gating at `240` rationale characters plus anchor coverage instead of warning-only behavior.
- Bundle automation profile metadata moved to `kiu.pipeline-profile/v0.3`, and empty trigger registries now surface an explicit warning.

## [0.3.0] - 2026-04-21

### Added
- `llm-assisted` drafting now performs real `Rationale` generation with prompt templates, provider abstraction, validator precheck, rejection logging, and token-budget tracking.
- `reports/rounds/*.json` now records auditable LLM prompt/response artifacts for drafting rounds.
- `scripts/show_profile.py` prints the fully resolved domain profile for one bundle.
- GitHub Actions CI now runs the unit test suite plus reference-bundle validation.
- `docs/kiu-skill-spec-v0.3.md` publishes the v0.3 public spec surface.
- `workflow_candidates/examples/dcf-basic-valuation/steps.yaml` provides a schema-first workflow artifact example.
- `docs/CONTRIBUTING.md` defines the current i18n and verification rules.

### Changed
- Renamed scheduler config from `autonomous_refiner` to `refinement_scheduler`.
- Kept backward-compatible YAML alias loading for legacy `autonomous_refiner` bundles, with a deprecation warning during profile resolution.
- Published skills now enforce domain-profile minimum evaluation counts (`20/20/10` for investing).
- Reference skill eval summaries now report shared-corpus full-release coverage while keeping representative sample case lists.
- Repo docs now use portable `python3` commands instead of machine-local interpreter paths.
