from __future__ import annotations

import re
from collections import Counter
from typing import Any


SCHEMA_VERSION = "kiu.action-skill-identity/v0.1"

PUBLISH_SKILL_THRESHOLD = 0.85
PUBLISH_GATEWAY_THRESHOLD = 0.75

ACTION_TERMS = (
    "decide",
    "decision",
    "judge",
    "judgment",
    "choose",
    "prioritize",
    "tradeoff",
    "boundary",
    "trigger",
    "next action",
    "disconfirmation",
    "verify",
    "risk",
    "when",
    "use when",
    "判断",
    "决策",
    "取舍",
    "边界",
    "触发",
    "行动",
    "下一步",
    "校验",
    "反证",
    "风险",
    "何时",
)

CONTAINER_PATTERNS: tuple[tuple[str, str, str], ...] = (
    ("exercise_material", r"练习题|自主练习|基本练习|习题|答案|quiz|exercise|problem set", "route_evaluation_material"),
    ("case_material", r"迷你案例|案例材料|case study|mini case", "route_case_library"),
    ("concept_container", r"关键概念|^概念$|术语|definition|glossary|key concept", "route_concept_note"),
    ("toolbox_container", r"工具箱|应用分析|toolbox|appendix|附录", "route_source_context"),
    ("summary_container", r"摘要|总结|overview|chapter summary|本章小结", "route_source_context"),
)


def derive_semantic_action_slug(label: str) -> str | None:
    """Map heading-like source labels to stable action-skill identities.

    This is intentionally a small semantic model rather than a title blacklist: the
    output names the action capability, not the source section title.
    """
    text = str(label or "").lower()
    if not text.strip():
        return None
    if _has_financial_value_screening_frame(text):
        return "price-value-screening-gate"
    if _has_accounting_quality_frame(text):
        return "accounting-quality-signal-check"
    if _has_business_value_anchor_frame(text):
        return "business-value-anchor-check"
    return None


def _has_financial_value_screening_frame(text: str) -> bool:
    has_security = any(term in text for term in ("股票", "stock", "equity", "证券"))
    has_selection = any(term in text for term in ("筛选", "选择", "select", "screen", "买入", "buy"))
    has_value_pressure = any(term in text for term in ("价值", "估值", "价格", "市盈率", "溢价", "漂亮", "value", "price", "valuation", "p/e", "premium", "nifty"))
    return has_security and has_selection and has_value_pressure


def _has_accounting_quality_frame(text: str) -> bool:
    has_accounting = any(term in text for term in ("会计", "盈余", "收益", "利润", "accounting", "earnings", "income"))
    has_quality = any(term in text for term in ("质量", "异常", "超常", "可持续", "quality", "abnormal", "sustainable"))
    return has_accounting and has_quality


def _has_business_value_anchor_frame(text: str) -> bool:
    has_business = any(term in text for term in ("企业", "业务", "经营", "business", "enterprise", "operating"))
    has_value = any(term in text for term in ("价值", "估值", "value", "valuation"))
    return has_business and has_value


def assess_action_skill_identity(seed: Any) -> dict[str, Any]:
    candidate_id = _candidate_id(seed)
    candidate_kind = _candidate_kind(seed)
    metadata = _metadata(seed)
    disposition = metadata.get("disposition")
    seed_content = _seed_content(seed)
    text = _candidate_text(seed)

    container_signals = _container_signals(candidate_id=candidate_id, text=text)
    is_gateway = candidate_id == "workflow-gateway" or candidate_kind == "workflow_gateway"
    is_workflow_candidate = disposition == "workflow_script_candidate" or candidate_kind == "workflow_script"

    dimension_scores = _dimension_scores(
        candidate_id=candidate_id,
        candidate_kind=candidate_kind,
        seed_content=seed_content,
        metadata=metadata,
        text=text,
        container_signals=container_signals,
        is_gateway=is_gateway,
        is_workflow_candidate=is_workflow_candidate,
    )
    score = round(sum(dimension_scores.values()) / len(dimension_scores), 4)
    primary_action_layer = _primary_action_layer(text)

    if is_gateway:
        route = "publish_gateway"
        route_reason = "workflow_gateway_entrypoint"
    elif is_workflow_candidate:
        route = "route_workflow_candidate"
        route_reason = "high_workflow_certainty_candidate_kept_outside_thick_skills"
    elif container_signals:
        route = _container_route(container_signals)
        route_reason = "source_value_container_without_sufficient_action_skill_identity"
    elif score >= PUBLISH_SKILL_THRESHOLD:
        route = "publish_skill"
        route_reason = "judgment_rich_action_skill_identity_meets_threshold"
    elif score >= 0.65:
        route = "route_source_context"
        route_reason = "partial_action_value_but_identity_below_publish_threshold"
    else:
        route = "reject"
        route_reason = "insufficient_action_value_and_identity"

    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": candidate_id,
        "candidate_kind": candidate_kind,
        "primary_action_layer": primary_action_layer,
        "action_skill_identity_score": score,
        "route": route,
        "dimension_scores": dimension_scores,
        "route_reason": route_reason,
        "container_signals": container_signals,
    }


def build_action_identity_report(
    seeds: list[Any],
    *,
    published_candidate_ids: list[str] | set[str] | None = None,
) -> dict[str, Any]:
    published = set(str(item) for item in (published_candidate_ids or []))
    candidates = [assess_action_skill_identity(seed) for seed in seeds]
    distribution = Counter(str(candidate["route"]) for candidate in candidates)
    published_non_gateway = [
        candidate
        for candidate in candidates
        if candidate["candidate_id"] in published and candidate["route"] != "publish_gateway"
    ]
    publishable = [candidate for candidate in published_non_gateway if candidate["route"] == "publish_skill"]
    leaked_containers = [
        candidate
        for candidate in published_non_gateway
        if candidate["route"] not in {"publish_skill", "publish_gateway"}
    ]
    scores = [float(candidate["action_skill_identity_score"]) for candidate in published_non_gateway]
    denominator = len(published_non_gateway)
    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_route_distribution": dict(sorted(distribution.items())),
        "container_candidate_leak_count": len(leaked_containers),
        "container_candidate_leaks": [candidate["candidate_id"] for candidate in leaked_containers],
        "publishable_action_skill_ratio": round(len(publishable) / denominator, 4) if denominator else 1.0,
        "minimum_action_skill_identity_score": round(min(scores), 4) if scores else None,
        "candidates": candidates,
    }


def _dimension_scores(
    *,
    candidate_id: str,
    candidate_kind: str,
    seed_content: dict[str, Any],
    metadata: dict[str, Any],
    text: str,
    container_signals: list[str],
    is_gateway: bool,
    is_workflow_candidate: bool,
) -> dict[str, float]:
    if is_gateway:
        return {
            "primary_action_layer_fit": 0.82,
            "judgment_trigger_clarity": 0.80,
            "user_context_requirement": 0.78,
            "action_value_output": 0.78,
            "boundary_and_misuse_control": 0.82,
            "feedback_or_disconfirmation": 0.70,
        }
    if is_workflow_candidate:
        return {
            "primary_action_layer_fit": 0.70,
            "judgment_trigger_clarity": 0.55,
            "user_context_requirement": 0.70,
            "action_value_output": 0.70,
            "boundary_and_misuse_control": 0.75,
            "feedback_or_disconfirmation": 0.55,
        }

    action_density = _term_density(text, ACTION_TERMS)
    has_trigger = _has_any(seed_content, ("trigger", "use_situation_trigger", "when_to_use")) or "use when" in text.lower()
    has_output = _has_any(seed_content, ("output", "next_action", "judgment_schema")) or re.search(
        r"next action|下一步|输出|建议|verdict|decision", text, flags=re.IGNORECASE
    )
    has_boundary = _has_any(seed_content, ("boundaries", "anti_conditions", "boundary", "do_not_fire_when")) or re.search(
        r"do not|不要|不用于|边界|misuse|滥用", text, flags=re.IGNORECASE
    )
    has_feedback = re.search(r"feedback|disconfirm|反证|复盘|校验|验证|命中率|premortem|pre-mortem", text, flags=re.IGNORECASE)
    context_need = re.search(r"context|constraint|situation|evidence|上下文|约束|证据|情境", text, flags=re.IGNORECASE)
    routing = metadata.get("routing_evidence", {}) if isinstance(metadata, dict) else {}
    routing = routing if isinstance(routing, dict) else {}
    agentic_priority = float(routing.get("agentic_priority", 0.0) or 0.0)
    matched_keyword_count = int(routing.get("matched_keyword_count", 0) or 0)
    case_density_score = float(routing.get("case_density_score", 0.0) or 0.0)
    routing_identity_bonus = 0.0
    if agentic_priority >= 2 and matched_keyword_count >= 2 and case_density_score >= 0.75:
        routing_identity_bonus = 0.18
    elif agentic_priority >= 1 and case_density_score >= 0.60:
        routing_identity_bonus = 0.10
    verification = metadata.get("verification", {}) if isinstance(metadata, dict) else {}
    verification = verification if isinstance(verification, dict) else {}
    verification_overall = float(verification.get("overall_score", 0.0) or 0.0)
    predictive_usefulness = float(verification.get("predictive_usefulness_score", 0.0) or 0.0)
    distinctiveness = float(verification.get("distinctiveness_score", 0.0) or 0.0)
    verification_identity_bonus = 0.0
    if verification_overall >= 0.90 and predictive_usefulness >= 0.85 and distinctiveness >= 0.75:
        verification_identity_bonus = 0.06
    container_penalty = 0.32 if container_signals else 0.0
    short_text_penalty = 0.10 if len(text.strip()) < 80 else 0.0
    identity_bonus = routing_identity_bonus + verification_identity_bonus

    return {
        "primary_action_layer_fit": _clamp(0.72 + action_density * 0.45 + identity_bonus - container_penalty - short_text_penalty),
        "judgment_trigger_clarity": _clamp(0.60 + (0.28 if has_trigger else 0.0) + action_density * 0.20 + identity_bonus - container_penalty),
        "user_context_requirement": _clamp(0.62 + (0.22 if context_need else 0.06) + identity_bonus / 2 - container_penalty / 2),
        "action_value_output": _clamp(0.62 + (0.24 if has_output else 0.0) + action_density * 0.20 + identity_bonus - container_penalty),
        "boundary_and_misuse_control": _clamp(0.58 + (0.28 if has_boundary else 0.0) + identity_bonus - container_penalty / 2),
        "feedback_or_disconfirmation": _clamp(0.60 + (0.24 if has_feedback else 0.08) + identity_bonus - container_penalty / 3),
    }


def _candidate_id(seed: Any) -> str:
    if isinstance(seed, dict):
        return str(seed.get("candidate_id") or seed.get("skill_id") or "")
    return str(getattr(seed, "candidate_id", ""))


def _candidate_kind(seed: Any) -> str:
    if isinstance(seed, dict):
        return str(seed.get("candidate_kind") or seed.get("kind") or "")
    return str(getattr(seed, "candidate_kind", ""))


def _metadata(seed: Any) -> dict[str, Any]:
    if isinstance(seed, dict):
        metadata = seed.get("metadata") or seed.get("candidate") or seed
    else:
        metadata = getattr(seed, "metadata", {})
    return metadata if isinstance(metadata, dict) else {}


def _seed_content(seed: Any) -> dict[str, Any]:
    if isinstance(seed, dict):
        content = seed.get("seed_content") or seed.get("content") or seed
    else:
        content = getattr(seed, "seed_content", {})
    return content if isinstance(content, dict) else {}


def _candidate_text(seed: Any) -> str:
    metadata = _metadata(seed)
    seed_content = _seed_content(seed)
    values: list[str] = [_candidate_id(seed), _candidate_kind(seed)]
    values.extend(_flatten_text(seed_content))
    values.extend(_flatten_text(metadata.get("contract", {})))
    values.extend(_flatten_text(metadata.get("workflow_gateway", {})))
    source_skill = getattr(seed, "source_skill", None)
    if source_skill is not None:
        values.extend(_flatten_text(getattr(source_skill, "sections", {})))
        values.extend(_flatten_text(getattr(source_skill, "contract", {})))
        values.extend(_flatten_text(getattr(source_skill, "scenario_families", {})))
        values.extend(_flatten_text(getattr(source_skill, "eval_summary", {})))
    return "\n".join(value for value in values if value).lower()


def _flatten_text(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        result: list[str] = []
        for key, child in value.items():
            result.append(str(key))
            result.extend(_flatten_text(child))
        return result
    if isinstance(value, (list, tuple, set)):
        result = []
        for child in value:
            result.extend(_flatten_text(child))
        return result
    if value is None:
        return []
    return [str(value)]


def _container_signals(*, candidate_id: str, text: str) -> list[str]:
    label_text = _label_text(candidate_id=candidate_id, text=text)
    haystack = label_text.lower()
    signals: list[str] = []
    for signal, pattern, _route in CONTAINER_PATTERNS:
        if re.search(pattern, haystack, flags=re.IGNORECASE):
            signals.append(signal)
    return signals


def _label_text(*, candidate_id: str, text: str) -> str:
    # Container identity must come from labels, not incidental words inside a rich skill body.
    labels = [candidate_id]
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("title") or stripped.startswith("skill_id") or stripped.startswith("candidate_id"):
            labels.append(stripped)
        if stripped.startswith("# ") and len(stripped) <= 80:
            labels.append(stripped)
    return "\n".join(labels)


def _container_route(signals: list[str]) -> str:
    for signal, _pattern, route in CONTAINER_PATTERNS:
        if signal in signals:
            return route
    return "route_source_context"


def _primary_action_layer(text: str) -> str:
    if re.search(r"signal|observe|scan|发现|观察|信号|雷达", text, flags=re.IGNORECASE):
        return "discover"
    if re.search(r"problem|reframe|define|why|jtbd|问题|定义|重构", text, flags=re.IGNORECASE):
        return "define"
    if re.search(r"feedback|disconfirm|复盘|反证|命中率", text, flags=re.IGNORECASE):
        return "feedback"
    return "resolve"


def _term_density(text: str, terms: tuple[str, ...]) -> float:
    matches = sum(1 for term in terms if term.lower() in text.lower())
    return min(matches / 8.0, 1.0)


def _has_any(doc: dict[str, Any], keys: tuple[str, ...]) -> bool:
    for key in keys:
        if key in doc and doc.get(key):
            return True
    return False


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)
