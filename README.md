# KiU · 学以致用

[![CI](https://github.com/rv198-star/rv198-start/actions/workflows/ci.yml/badge.svg)](https://github.com/rv198-star/rv198-start/actions/workflows/ci.yml)

KiU (`学以致用`) turns source knowledge into usable judgment.

It is not a summary engine, quote database, translator, or generic RAG notebook. KiU preserves what the source says, then distills bounded skills that help users judge, choose, refuse, act, or recalibrate.

Two rules define the project:

- `技能不是摘要`: a skill must be usable judgment, not a compressed chapter summary.
- `用而不染`: application context may gate or caveat use, but it must not rewrite the source-derived skill.

## Architecture

```text
Book -> Read Accurately -> Distill Judgment -> Skill or Workflow -> Calibrate Use -> Verify Value
```

| Step | What it means |
| --- | --- |
| 读准原书 | Preserve source passages, claims, structure, anchors, and provenance. |
| 提炼判断 | Distill transferable judgment from the source without reducing the book to notes. |
| 生成技能 | Publish only skills that help users judge, choose, refuse, act, or recalibrate. |
| 分流流程 | Keep deterministic procedures as workflows instead of inflating them into skills. |
| 校准应用 | Add isolated context, current-fact checks, caveats, and safety gates when needed. |
| 验证价值 | Evaluate whether outputs create action value at the stated evidence level. |

## Start Here

- [Project Architecture Narrative](docs/project-architecture-narrative.md)
- [Concept Language Glossary](docs/concept-language-glossary.md)
- [User-Facing Evaluation Guide](docs/user-facing-evaluation-guide.md)
- [Usage Guide](docs/usage-guide.md)
- [Backlog Board](backlog/board.yaml)
- [KiU Skill Spec v0.6](docs/kiu-skill-spec-v0.6.md)
- [Reference Bundle](bundles/poor-charlies-almanack-v0.1/manifest.yaml)
- [Engineering Reference Bundle](bundles/engineering-postmortem-v0.1/manifest.yaml)

## Current Evidence Boundary

The current project has strong internal generation, routing, and evaluation evidence. External blind review, real-user validation, and domain-expert validation remain separate evidence levels and should not be inferred from internal scores.

Install locally:

```bash
python3 -m pip install -e .
```

Validate locally:

```bash
python3 scripts/validate_bundle.py bundles/poor-charlies-almanack-v0.1
python3 scripts/show_profile.py bundles/poor-charlies-almanack-v0.1
python3 scripts/show_backlog.py --version v0.6.0
python3 -m unittest tests/test_validator.py
```

If validation returns an error such as
`circle-of-competence: rationale_below_density_threshold (...)`,
the published skill text is below the domain profile's hard density floor and must be revised before release.

Build a refinement-scheduled candidate bundle:

```bash
python3 scripts/build_candidates.py \
  --source-bundle bundles/poor-charlies-almanack-v0.1 \
  --run-id phase2-smoke
```

Review a generated run across source bundle, generated bundle, and usage outputs:

```bash
python3 scripts/review_generated_run.py \
  --run-root /tmp/kiu-local-artifacts/generated/poor-charlies-almanack-v0.1/phase2-smoke \
  --source-bundle bundles/poor-charlies-almanack-v0.1
```

By default, pipeline output is written outside the repo to `/tmp/kiu-local-artifacts/generated/`.
Set `KIU_LOCAL_OUTPUT_ROOT=/your/path` to override the fixed local root, or pass
`--output-root` if you intentionally want another location such as `generated/`.

Generate deterministic seed bundles only:

```bash
python3 scripts/generate_candidates.py \
  --source-bundle bundles/poor-charlies-almanack-v0.1 \
  --run-id local-v0_2 \
  --drafting-mode deterministic
```

Run one `llm-assisted` drafting pass with a mock provider:

```bash
KIU_LLM_PROVIDER=mock \
KIU_LLM_MOCK_RESPONSE="Replace me with a dense rationale.[^anchor:demo] [^trace:canonical/demo.yaml]" \
python3 scripts/build_candidates.py \
  --source-bundle bundles/poor-charlies-almanack-v0.1 \
  --run-id phase3-llm \
  --drafting-mode llm-assisted \
  --llm-budget-tokens 4000
```
