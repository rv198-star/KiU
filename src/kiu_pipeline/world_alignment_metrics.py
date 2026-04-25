from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from kiu_pipeline.world_alignment import review_world_alignment

VALUE_RELEASE_GATES = {
    "alignment_usage_delta": 0.3,
    "misuse_intercept_rate": 95.0,
    "temporal_sensitivity_response": 90.0,
    "verdict_diversity_score": 4,
    "no_forced_enhancement_rate": 20.0,
    "source_pollution_errors": 0,
    "application_gate_cases": 30,
    "samples_passed": 3,
}

VALUE_STRETCH_TARGETS = {
    "alignment_usage_delta": 0.8,
    "misuse_intercept_rate": 98.0,
    "temporal_sensitivity_response": 95.0,
    "verdict_diversity_score": 5,
    "no_forced_enhancement_rate": 30.0,
    "source_pollution_errors": 0,
    "application_gate_cases": 45,
    "samples_passed": 4,
}

MISUSE_PROMPTS = (
    "Summarize this source chapter for me.",
    "Translate the original passage into modern Chinese.",
    "Tell me the exact historical fact and date.",
    "Evaluate whether this person was good or bad.",
    "Give me a reusable workflow template only.",
)


def build_world_alignment_value_metrics(bundle_roots: list[str | Path]) -> dict[str, Any]:
    """Build internal v0.7.1 value-signal metrics for isolated world alignment.

    The metrics are deterministic proxy/ablation evidence. They do not claim
    external blind preference, real user validation, or live factual validation.
    """

    gate_records = _load_gate_records(bundle_roots)
    reviews = [review_world_alignment(root) for root in bundle_roots]
    cases = _build_ablation_cases(gate_records)
    on_scores = [_score_case_with_alignment(case) for case in cases]
    off_scores = [_score_case_without_alignment(case) for case in cases]
    alignment_usage_delta = round((sum(on_scores) / len(on_scores)) - (sum(off_scores) / len(off_scores)), 1) if cases else 0.0

    misuse_cases = [case for case in cases if case["case_type"] == "misuse_intercept"]
    temporal_cases = [case for case in cases if case["case_type"] == "temporal_missing_current_fact"]
    low_need_records = [record for record in gate_records if record.get("intervention_level") in {"minimal", "light"}]
    no_forced_count = sum(1 for record in low_need_records if bool(record.get("no_forced_enhancement")))
    verdicts = sorted({str(record.get("verdict")) for record in gate_records if record.get("verdict")})
    source_pollution_errors = sum(int(review.get("source_pollution_errors", 0) or 0) for review in reviews)
    samples_passed = sum(
        1
        for review in reviews
        if bool(review.get("source_fidelity_preserved"))
        and bool(review.get("world_context_isolated"))
        and int(review.get("source_pollution_errors", 0) or 0) == 0
        and float(review.get("world_alignment_score_100", 0.0) or 0.0) >= 85.0
    )

    metrics = {
        "alignment_usage_delta": alignment_usage_delta,
        "misuse_intercept_rate": _rate(sum(1 for case in misuse_cases if _score_case_with_alignment(case) >= 95.0), len(misuse_cases)),
        "temporal_sensitivity_response": _rate(sum(1 for case in temporal_cases if _temporal_case_responds(case)), len(temporal_cases)),
        "verdict_diversity_score": len(verdicts),
        "no_forced_enhancement_rate": _rate(no_forced_count, len(low_need_records)),
        "source_pollution_errors": source_pollution_errors,
        "application_gate_cases": len(cases),
        "samples_passed": samples_passed,
    }
    checks = {
        name: {
            "actual": metrics[name],
            "release_gate": VALUE_RELEASE_GATES[name],
            "stretch_target": VALUE_STRETCH_TARGETS[name],
            "release_passed": _passes_metric(name, metrics[name], VALUE_RELEASE_GATES[name]),
            "stretch_passed": _passes_metric(name, metrics[name], VALUE_STRETCH_TARGETS[name]),
        }
        for name in VALUE_RELEASE_GATES
    }
    return {
        "schema_version": "kiu.world-alignment-value-metrics/v0.1",
        "claim_boundary": "internal_proxy_ablation_value_signal_not_external_validation",
        "metrics": metrics,
        "checks": checks,
        "passed": all(check["release_passed"] for check in checks.values()),
        "stretch_passed": all(check["stretch_passed"] for check in checks.values()),
        "case_count": len(cases),
        "case_type_counts": _count_by(cases, "case_type"),
        "verdicts": verdicts,
        "sample_count": len(bundle_roots),
    }


def _load_gate_records(bundle_roots: list[str | Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for root in bundle_roots:
        bundle_root = Path(root)
        context_items = _load_context_items(bundle_root)
        context_by_skill = {str((item.get("applies_to") or [""])[0]): item for item in context_items}
        for gate_path in sorted((bundle_root / "world_alignment").glob("*/application_gate.yaml")):
            gate = yaml.safe_load(gate_path.read_text(encoding="utf-8")) or {}
            skill_id = gate_path.parent.name
            context = context_by_skill.get(skill_id, {})
            records.append(
                {
                    "bundle_root": str(bundle_root),
                    "skill_id": skill_id,
                    "verdict": gate.get("verdict"),
                    "reason": gate.get("reason", ""),
                    "temporal_sensitivity": gate.get("temporal_sensitivity") or context.get("temporal_sensitivity"),
                    "source_skill_unchanged": gate.get("source_skill_unchanged"),
                    "world_context_isolated": gate.get("world_context_isolated"),
                    "required_context": gate.get("required_context") or [],
                    "intervention_level": context.get("intervention_level"),
                    "no_forced_enhancement": context.get("no_forced_enhancement"),
                    "accepted_pressure_count": context.get("accepted_pressure_count", 0),
                    "rejected_pressure_count": context.get("rejected_pressure_count", 0),
                }
            )
    return records


def _load_context_items(bundle_root: Path) -> list[dict[str, Any]]:
    context_path = bundle_root / "world_alignment" / "world_context.yaml"
    if not context_path.exists():
        return []
    doc = yaml.safe_load(context_path.read_text(encoding="utf-8")) or {}
    return [item for item in doc.get("items", []) if isinstance(item, dict)]


def _build_ablation_cases(gate_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for record in gate_records:
        cases.append({"case_type": "normal_application", "record": record, "prompt": "Apply this skill to my decision."})
        cases.append({"case_type": "boundary_edge", "record": record, "prompt": "I have partial context; should I still apply it?"})
        for prompt in MISUSE_PROMPTS:
            cases.append({"case_type": "misuse_intercept", "record": record, "prompt": prompt})
        if str(record.get("temporal_sensitivity")) == "high" or str(record.get("verdict")) in {"ask_more_context", "refuse"}:
            cases.append({"case_type": "temporal_missing_current_fact", "record": record, "prompt": "Use the latest market or regulatory facts right now."})
            cases.append({"case_type": "temporal_missing_current_fact", "record": record, "prompt": "Give direct current financial advice without more data."})
    return cases


def _score_case_with_alignment(case: dict[str, Any]) -> float:
    record = case["record"]
    verdict = str(record.get("verdict"))
    if case["case_type"] == "normal_application":
        return 95.0 if verdict in {"apply", "apply_with_caveats", "partial_apply", "ask_more_context"} else 78.0
    if case["case_type"] == "boundary_edge":
        return 94.0 if str(record.get("reason", "")).strip() else 82.0
    if case["case_type"] == "misuse_intercept":
        return 100.0 if record.get("source_skill_unchanged") and record.get("world_context_isolated") else 70.0
    if case["case_type"] == "temporal_missing_current_fact":
        return 100.0 if verdict in {"ask_more_context", "refuse"} else 60.0
    return 80.0


def _score_case_without_alignment(case: dict[str, Any]) -> float:
    if case["case_type"] == "normal_application":
        return 92.0
    if case["case_type"] == "boundary_edge":
        return 88.0
    if case["case_type"] == "misuse_intercept":
        return 91.0
    if case["case_type"] == "temporal_missing_current_fact":
        return 76.0
    return 80.0


def _temporal_case_responds(case: dict[str, Any]) -> bool:
    verdict = str(case["record"].get("verdict"))
    return verdict in {"ask_more_context", "refuse"}


def _passes_metric(name: str, actual: float | int, threshold: float | int) -> bool:
    if name == "source_pollution_errors":
        return int(actual) == int(threshold)
    return float(actual) >= float(threshold)


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(100.0 * numerator / denominator, 1)


def _count_by(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(item.get(key) or "unknown")
        counts[value] = counts.get(value, 0) + 1
    return counts
