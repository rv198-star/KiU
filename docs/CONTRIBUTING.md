# Contributing

## i18n Policy

KiU v0.3 uses a simple language split:

- spec and API-facing docs: English canonical
- user guides and operational docs: bilingual or Chinese-first is acceptable when no English pair exists yet
- bundle content: controlled by each bundle's `manifest.language`

For new docs:

- add new normative specs in English first
- keep CLI examples portable (`python3`, not machine-local absolute paths)
- when a user-facing guide is expanded materially, prefer keeping an English canonical version and adding Chinese explanatory guidance where needed

## Validation Before Change

Install the repo into a local environment first:

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

Before submitting changes, run:

```bash
.venv/bin/python -m unittest tests/test_profile_resolver.py
.venv/bin/python -m unittest tests/test_validator.py
.venv/bin/python -m unittest tests/test_pipeline.py
.venv/bin/python -m unittest tests/test_refiner.py
.venv/bin/python scripts/validate_bundle.py bundles/poor-charlies-almanack-v0.1
```

## Release Hygiene

For release-facing changes, keep these rules explicit:

- update `CHANGELOG.md` in the same branch as the code or bundle change
- if a revision was manually rewritten, say so in `iterations/revisions.yaml` and `SKILL.md`
- only call a revision "loop-driven" when `refinement_scheduler` actually ran
- generated candidate `SKILL.md` summaries must stay synced with `eval/summary.yaml` and `iterations/revisions.yaml`
