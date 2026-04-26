# Examples

This directory holds development examples and regression inputs. Current reviewer-facing
generated artifacts live in `review-pack/current/`, not here.

## Fixture Bundles

- `fixtures/effective-requirements-analysis.yaml`
- `fixtures/financial-statement-analysis.yaml`

The fixture YAML files remain useful for deterministic pipeline smoke tests.

## Source Materials

`source-materials/` contains book/source inputs used by regression runs and historical
generation checks.

- `source-materials/有效需求分析（第2版）.md`
  - engineering/product analysis leaning sample
- `source-materials/财务报表分析_Markdown版.md`
  - finance/accounting analysis leaning sample
- `source-materials/shiji_md/`
  - historical source corpus sample
- `source-materials/MaoZeDongAnthology-master/`
  - political theory source corpus sample

These source materials are independent source/extraction regression inputs and are not mixed into a single skill bundle.

## Legacy Materials

`legacy/` contains historical example artifacts that are kept for traceability but are
not the current reviewer entry point.
