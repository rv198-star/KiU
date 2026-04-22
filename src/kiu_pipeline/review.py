from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .preflight import validate_generated_bundle
from kiu_validator.core import validate_bundle


def review_generated_run(
    *,
    run_root: str | Path,
    source_bundle_path: str | Path,
    usage_review_dir: str | Path | None = None,
) -> dict[str, Any]:
    run_root = Path(run_root)
    bundle_root = run_root / "bundle"
    usage_root = Path(usage_review_dir) if usage_review_dir is not None else run_root / "usage-review"

    source_report = validate_bundle(source_bundle_path)
    generated_report = validate_generated_bundle(bundle_root)
    metrics = _load_json(run_root / "reports" / "metrics.json")
    production_quality = _load_json(run_root / "reports" / "production-quality.json")
    usage_docs = _load_usage_reviews(usage_root)
    usage_docs = [
        doc
        for doc in usage_docs
        if _belongs_to_run(doc, run_root)
    ]

    source_bundle = _score_source_bundle(source_report)
    generated_bundle = _score_generated_bundle(
        generated_report=generated_report,
        production_quality=production_quality,
        metrics=metrics,
        run_root=run_root,
    )
    usage_outputs = _score_usage_outputs(usage_docs)

    overall_score = round(
        0.30 * source_bundle["score_100"]
        + 0.40 * generated_bundle["score_100"]
        + 0.30 * usage_outputs["score_100"],
        1,
    )

    return {
        "run_root": str(run_root),
        "source_bundle_path": str(Path(source_bundle_path)),
        "usage_review_dir": str(usage_root),
        "source_bundle": source_bundle,
        "generated_bundle": generated_bundle,
        "usage_outputs": usage_outputs,
        "overall_score_100": overall_score,
    }


def _score_source_bundle(report: dict[str, Any]) -> dict[str, Any]:
    errors = report.get("errors", [])
    warnings = report.get("warnings", [])
    graph = report.get("graph", {})
    shared = report.get("shared_assets", {})
    manifest = report.get("manifest", {})
    skills = report.get("skills", [])

    structural_cleanliness = max(0.0, 1.0 - 0.25 * len(errors))
    warning_cleanliness = max(0.0, 1.0 - 0.10 * len(warnings))
    graph_factor = _ratio(
        [
            1.0 if graph.get("node_count", 0) > 0 else 0.0,
            1.0 if graph.get("edge_count", 0) > 0 else 0.0,
            1.0 if graph.get("community_count", 0) > 0 else 0.0,
        ]
    )
    asset_factor = _ratio(
        [
            1.0 if len(manifest.get("skills", [])) > 0 else 0.0,
            1.0 if shared.get("trace_count", 0) > 0 else 0.0,
            1.0 if shared.get("evaluation_count", 0) > 0 else 0.0,
        ]
    )
    maturity_factor = _score_source_skill_maturity(skills)
    score = round(
        100.0
        * (
            0.40 * structural_cleanliness
            + 0.10 * warning_cleanliness
            + 0.10 * graph_factor
            + 0.15 * asset_factor
            + 0.25 * maturity_factor
        ),
        1,
    )
    notes: list[str] = []
    if not errors and not warnings:
        notes.append("validator_clean")
    if shared.get("trace_count", 0) > 0 and shared.get("evaluation_count", 0) > 0:
        notes.append("shared_evidence_pool_present")

    return {
        "score_100": score,
        "errors": len(errors),
        "warnings": len(warnings),
        "skill_count": len(manifest.get("skills", [])),
        "graph": graph,
        "shared_assets": shared,
        "maturity_factor": round(maturity_factor, 4),
        "notes": notes,
    }


def _score_generated_bundle(
    *,
    generated_report: dict[str, Any],
    production_quality: dict[str, Any],
    metrics: dict[str, Any],
    run_root: Path,
) -> dict[str, Any]:
    errors = generated_report.get("errors", [])
    warnings = generated_report.get("warnings", [])
    workflow_count = int(metrics.get("summary", {}).get("workflow_script_candidates", 0) or 0)
    workflow_dirs = len(
        [path for path in (run_root / "workflow_candidates").glob("*") if path.is_dir()]
    ) if (run_root / "workflow_candidates").exists() else 0
    boundary_preserved = workflow_count == 0 or workflow_dirs == workflow_count

    structural_cleanliness = max(0.0, 1.0 - 0.25 * len(errors) - 0.05 * len(warnings))
    minimum_production = float(production_quality.get("minimum_production_quality", 0.0) or 0.0)
    average_production = float(production_quality.get("average_production_quality", 0.0) or 0.0)
    workflow_boundary_factor = 1.0 if boundary_preserved else 0.0
    score = round(
        100.0
        * (
            0.65 * minimum_production
            + 0.15 * average_production
            + 0.10 * structural_cleanliness
            + 0.10 * workflow_boundary_factor
        ),
        1,
    )

    notes: list[str] = []
    if production_quality.get("bundle_quality_grade") == "excellent":
        notes.append("production_quality_excellent")
    if workflow_count > 0 and boundary_preserved:
        notes.append("workflow_boundary_preserved")
    if workflow_count > 0 and not boundary_preserved:
        notes.append("workflow_boundary_drift")

    return {
        "score_100": score,
        "errors": len(errors),
        "warnings": len(warnings),
        "skill_count": int(production_quality.get("candidate_count", 0) or 0),
        "workflow_candidate_count": workflow_count,
        "bundle_quality_grade": production_quality.get("bundle_quality_grade"),
        "minimum_production_quality": minimum_production,
        "average_production_quality": average_production,
        "notes": notes,
    }


def _score_usage_outputs(docs: list[dict[str, Any]]) -> dict[str, Any]:
    scored_docs = [_score_usage_doc(doc) for doc in docs if _is_skill_usage_doc(doc)]
    if not scored_docs:
        return {
            "score_100": 0.0,
            "sample_count": 0,
            "notes": ["no_skill_usage_reviews_found"],
            "samples": [],
        }

    average_doc_score = sum(item["score_100"] for item in scored_docs) / len(scored_docs)
    coverage_factor = min(len(scored_docs) / 3.0, 1.0)
    score = round(0.85 * average_doc_score + 15.0 * coverage_factor, 1)
    return {
        "score_100": score,
        "sample_count": len(scored_docs),
        "notes": ["usage_reviews_scored"],
        "samples": scored_docs,
    }


def _score_usage_doc(doc: dict[str, Any]) -> dict[str, Any]:
    quality = doc.get("quality_assessment", {})
    structured_output = doc.get("structured_output", {})
    contract_fit_map = {
        "strong": 1.0,
        "medium": 0.75,
        "weak": 0.45,
    }
    contract_fit = contract_fit_map.get(str(quality.get("contract_fit", "")).lower(), 0.4)

    boundary_status = str(doc.get("boundary_check", {}).get("status", "")).lower()
    boundary_score = {
        "pass": 1.0,
        "warning": 0.6,
        "fail": 0.2,
    }.get(boundary_status, 0.4)

    structured_score = min(len(structured_output) / 3.0, 1.0) if structured_output else 0.0
    evidence_score = min(len(quality.get("evidence_alignment", []) or []) / 3.0, 1.0)

    scenario_score = 0.0
    if isinstance(doc.get("input_scenario"), dict) and doc["input_scenario"]:
        scenario_score += 0.5
    if doc.get("analysis_summary"):
        scenario_score += 0.25
    firing = doc.get("firing_assessment", {})
    if isinstance(firing, dict) and "should_fire" in firing:
        scenario_score += 0.25

    score = round(
        100.0
        * (
            0.30 * contract_fit
            + 0.20 * boundary_score
            + 0.20 * structured_score
            + 0.15 * evidence_score
            + 0.15 * min(scenario_score, 1.0)
        ),
        1,
    )
    return {
        "review_case_id": doc.get("review_case_id", "<missing-review-case-id>"),
        "score_100": score,
        "skill_path": doc.get("skill_path"),
    }


def _is_skill_usage_doc(doc: dict[str, Any]) -> bool:
    return bool(doc.get("skill_path")) and isinstance(doc.get("structured_output"), dict)


def _load_usage_reviews(root: Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    docs: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.yaml")):
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(loaded, dict):
            loaded["_path"] = str(path)
            docs.append(loaded)
    return docs


def _belongs_to_run(doc: dict[str, Any], run_root: Path) -> bool:
    generated_run_root = doc.get("generated_run_root")
    if not generated_run_root:
        return True
    try:
        return Path(generated_run_root).resolve() == run_root.resolve()
    except OSError:
        return False


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def _ratio(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _score_source_skill_maturity(skills: list[dict[str, Any]]) -> float:
    if not skills:
        return 0.0

    status_weights = {
        "published": 1.0,
        "under_evaluation": 0.7,
        "candidate": 0.55,
        "archived": 0.8,
    }
    maturity_scores: list[float] = []
    for skill in skills:
        status_score = status_weights.get(str(skill.get("status", "")).lower(), 0.4)
        eval_counts = skill.get("eval_case_counts", {})
        total_eval_cases = sum(int(value or 0) for value in eval_counts.values())
        eval_score = min(total_eval_cases / 20.0, 1.0)
        revision_score = 1.0 if skill.get("has_revision_loop") else 0.5
        maturity_scores.append(
            0.60 * status_score + 0.25 * eval_score + 0.15 * revision_score
        )
    return _ratio(maturity_scores)
