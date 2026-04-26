# KiU Skill Spec v0.4

KiU v0.4 extends the v0.3 bundle and pipeline surface in one specific direction:
it hardens the **single-domain production line**. This version does **not** yet define
cross-bundle graph merge, second-domain validation, or a completed proof of autonomous
refinement. Those remain v0.5 work.

## Positioning

v0.4 is about four concrete upgrades:

- honest published-skill density and release gates
- production-quality grading for generated candidate bundles
- example fixtures as lightweight second-line source inputs
- honest rendering rules so thick markdown views cannot drift away from structured truth docs

## Bundle and Profile Surface

The published bundle shape is unchanged from v0.3:

```text
bundle/
├── manifest.yaml
├── automation.yaml
├── graph/graph.json
├── skills/<skill-id>/
│   ├── SKILL.md
│   ├── anchors.yaml
│   ├── eval/summary.yaml
│   └── iterations/revisions.yaml
├── traces/
├── evaluation/
└── sources/
```

`automation.yaml` selects its resolved profile via:

- `inherits_from` (preferred)
- `inherits` (compatibility alias)

If both are present, they must agree.

## Workflow-vs-Agentic Boundary

v0.4 keeps the routing decision inside the profile instead of pushing it into an
implicit runtime heuristic.

The current model uses:

- `workflow_certainty`
- `context_certainty`
- profile `routing_rules`

When both workflow certainty and context certainty are high, the node should degrade
to `workflow_script_candidate` and stay outside `bundle/skills/`. The candidate is still
preserved for audit under `workflow_candidates/`.

When the task still needs judgment-rich interpretation, the node remains a
`skill_candidate` and is materialized into the generated bundle.

## Published Skill Gates

v0.4 keeps all v0.3 published-skill gates and makes them operationally stricter:

- double anchoring must remain valid
- all three evaluation subsets must pass
- subset counts must satisfy the domain profile minimums
- published skills must pass the profile-defined density gate
- at least one revision cycle must exist
- at least three usage trace references must remain attached

For the investing profile, density is a hard gate:

- rationale minimum: `240` characters
- rationale minimum anchor refs: `2`
- evidence-summary minimum anchor refs: `1`

## Honest Thick Views

`SKILL.md` remains the human-facing thick view, but v0.4 clarifies that it is **not**
the authoritative source for generated candidate state.

For generated bundles:

- `Evaluation Summary` must be rendered from `eval/summary.yaml`
- `Revision Summary` must be rendered from `iterations/revisions.yaml`
- preflight must fail if either markdown section drifts away from its structured source

This prevents the exact failure mode where a candidate's markdown claims a pass state
that its YAML truth doc does not support.

## Production Quality Gating

v0.4 adds a second layer beyond structural validation.

Each domain profile may define `refinement_scheduler.release_quality`:

- score weights
- minimum `artifact_quality`
- minimum `production_quality`

The generated run should emit a bundle-level quality report that records:

- per-skill `artifact_quality`
- per-skill `production_quality`
- minimum bundle-wide production quality
- bundle quality grade
- release readiness flag

This gate says the generated artifacts reached the current production-line bar.
It does **not** prove a real host runtime or dispatcher has already been validated.

## Example Fixtures

v0.4 introduces example fixtures as lightweight, reproducible source lines:

- fixture YAML in `examples/fixtures/`
- compact source markdown in `examples/sources/`
- scaffolded source bundle under a local output root
- generated candidate bundle derived from that scaffolded source bundle

Fixtures are intended for smoke testing, packaging checks, and quality review. They are
not published reference bundles and should not be confused with the canonical release
bundle under `bundles/`.

By default, generated fixture artifacts live outside the repo:

- `/tmp/kiu-local-artifacts/generated/`
- `/tmp/kiu-local-artifacts/sources/`

## Revision Honesty

v0.4 draws a strict distinction between:

- manual content upgrades
- refinement-scheduler loop output

If a revision was produced by manual rewriting, the revision log and any markdown summary
must say so directly. A revision may only be described as loop-driven when the
`refinement_scheduler` actually executed and the resulting evidence is preserved in run
artifacts.

## Out of Scope

The following items are intentionally outside the v0.4 public surface:

- second-domain published bundle validation
- cross-bundle graph merge
- validator `--merge-with` release workflow
- proof that autonomous refinement materially improves at least two shipped skills

Those items define the next milestone rather than this one.
