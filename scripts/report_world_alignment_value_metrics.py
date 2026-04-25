#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import yaml

from kiu_pipeline.world_alignment import build_world_alignment_artifacts
from kiu_pipeline.world_alignment_metrics import build_world_alignment_value_metrics

SAMPLE_BUNDLES = {
    "poor_charlie_principles": {
        "circle-of-competence": "Circle Of Competence",
        "invert-the-problem": "Invert The Problem",
        "bias-self-audit": "Bias Self Audit",
        "value-assessment-source-note": "Value Assessment Source Note",
        "role-boundary-before-action": "Role Boundary Before Action",
    },
    "effective_requirements_methods": {
        "business-first-subsystem-decomposition": "Business First Subsystem Decomposition",
        "stakeholder-conflict-clarification": "Stakeholder Conflict Clarification",
    },
    "financial_statement_current_context": {
        "financial-statement-current-investment-check": "Financial Statement Current Investment Check",
        "challenge-price-with-value": "Challenge Price With Value",
    },
    "no_web_refuse_fixture": {
        "current-investment-advice": "Current Investment Advice",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate v0.7.1 world-alignment value metrics.")
    parser.add_argument("--workdir", default="/tmp/kiu-v071-world-alignment-value", help="Directory for generated sample bundles.")
    parser.add_argument("--output", required=True, help="Markdown report output path.")
    parser.add_argument("--json-output", help="Optional JSON metrics output path.")
    args = parser.parse_args()

    workdir = Path(args.workdir)
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    bundles = []
    for sample_id, skills in SAMPLE_BUNDLES.items():
        bundle = _write_sample_bundle(workdir / sample_id, skills)
        build_world_alignment_artifacts(bundle, no_web_mode=True)
        bundles.append(bundle)

    metrics = build_world_alignment_value_metrics(bundles)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(_render_markdown(metrics), encoding="utf-8")
    if args.json_output:
        json_path = Path(args.json_output)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": metrics["passed"], "stretch_passed": metrics["stretch_passed"], "output": str(output)}, ensure_ascii=False))
    return 0 if metrics["passed"] else 1


def _write_sample_bundle(root: Path, skills: dict[str, str]) -> Path:
    bundle = root / "bundle"
    (bundle / "skills").mkdir(parents=True, exist_ok=True)
    manifest_skills = []
    for skill_id, title in skills.items():
        skill_dir = bundle / "skills" / skill_id
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_text = (
            f"# {title}\n\n"
            f"## Identity\n```yaml\nskill_id: {skill_id}\ntitle: {title}\n```\n\n"
            "## Rationale\nSource-faithful rationale only.\n\n"
            "## Usage Summary\nUse the source-derived skill within its native boundary.\n"
        )
        (skill_dir / "SKILL.md").write_text(skill_text, encoding="utf-8")
        manifest_skills.append({"skill_id": skill_id, "path": f"skills/{skill_id}"})
    (bundle / "manifest.yaml").write_text(
        yaml.safe_dump({"bundle_id": root.name, "skills": manifest_skills}, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return bundle


def _render_markdown(metrics: dict) -> str:
    lines = [
        "# v0.7.1 World Alignment Value Metrics",
        "",
        "This report is internal proxy and ablation evidence. It does not claim external blind preference, real-user validation, live-web factual correctness, domain-expert validation, or multi-world modeling.",
        "",
        f"Release gate: {'PASS' if metrics['passed'] else 'FAIL'}",
        f"Stretch target: {'PASS' if metrics['stretch_passed'] else 'PARTIAL'}",
        "",
        "## Value Metric Scorecard",
        "",
        "| Metric | Actual | Release Gate | Release | Stretch Target | Stretch |",
        "| --- | ---: | ---: | --- | ---: | --- |",
    ]
    for name, check in metrics["checks"].items():
        lines.append(
            f"| `{name}` | `{check['actual']}` | `{check['release_gate']}` | {'PASS' if check['release_passed'] else 'FAIL'} | `{check['stretch_target']}` | {'PASS' if check['stretch_passed'] else 'MISS'} |"
        )
    lines.extend([
        "",
        "## Case Mix",
        "",
        f"Total proxy/ablation cases: `{metrics['case_count']}`",
        "",
        "| Case Type | Count |",
        "| --- | ---: |",
    ])
    for case_type, count in sorted(metrics["case_type_counts"].items()):
        lines.append(f"| `{case_type}` | {count} |")
    lines.extend([
        "",
        "## Verdict Coverage",
        "",
        ", ".join(f"`{verdict}`" for verdict in metrics["verdicts"]),
        "",
        "## Interpretation",
        "",
        "The release gate proves internal value signals only: world alignment improves deterministic proxy/ablation handling for known misuse, temporal missing-context cases, verdict diversity, and low-need no-forced-enhancement behavior. It does not prove real user preference or factual correctness about the current world.",
        "",
    ])
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
