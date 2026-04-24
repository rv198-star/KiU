from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .load import extract_yaml_section, parse_sections
from .render import load_generated_candidates


def write_smoke_usage_reviews(run_root: Path) -> None:
    """Emit source-backed smoke usage reviews for generated skill candidates."""
    bundle_root = run_root / "bundle"
    usage_root = run_root / "usage-review"
    usage_root.mkdir(parents=True, exist_ok=True)
    candidates = load_generated_candidates(bundle_root)
    for candidate in candidates:
        skill_id = candidate["candidate"]["candidate_id"]
        anchors = candidate.get("anchors", {})
        source_anchors = anchors.get("source_anchor_sets", [])
        primary_anchor = source_anchors[0] if source_anchors else {}
        secondary_anchor = source_anchors[1] if len(source_anchors) > 1 else primary_anchor
        sections = parse_sections(candidate.get("skill_markdown", ""))
        contract = extract_yaml_section(sections.get("Contract", ""))
        trigger_patterns = [
            item
            for item in contract.get("trigger", {}).get("patterns", [])
            if isinstance(item, str)
        ]
        output_schema = (
            contract.get("judgment_schema", {})
            .get("output", {})
            .get("schema", {})
        )
        verdict = output_schema.get("verdict", "apply")
        if skill_id == "workflow-gateway":
            _write_workflow_gateway_usage_reviews(
                usage_root=usage_root,
                run_root=run_root,
                bundle_root=bundle_root,
                candidate=candidate,
                source_anchors=source_anchors,
                trigger_patterns=trigger_patterns,
            )
            continue

        evidence_to_check = _derive_smoke_evidence_to_check(
            primary_anchor=primary_anchor,
            secondary_anchor=secondary_anchor,
            trigger_patterns=trigger_patterns,
        )
        next_action = _derive_specific_next_action(
            skill_id=skill_id,
            verdict=verdict if isinstance(verdict, str) else "apply",
            primary_anchor=primary_anchor,
            secondary_anchor=secondary_anchor,
        )
        usage_doc = {
            "review_case_id": f"{skill_id}-smoke-usage",
            "generated_run_root": str(run_root),
            "skill_path": str(bundle_root / "skills" / skill_id / "SKILL.md"),
            "input_scenario": {
                "scenario": primary_anchor.get("snippet", ""),
                "decision_goal": f"Decide whether `{skill_id}` should fire for this source-backed situation.",
                "decision_scope": (
                    f"Only use `{skill_id}` for the decision boundary implied by "
                    f"`{primary_anchor.get('anchor_id', skill_id)}`."
                ),
                "current_constraints": [
                    f"Confirm the scenario still satisfies `{trigger_patterns[0]}`."
                ] if trigger_patterns else [],
                "disconfirming_evidence": [
                    (
                        "Do not apply if new facts contradict the primary evidence "
                        f"anchored at `{primary_anchor.get('anchor_id', skill_id)}`."
                    )
                ],
            },
            "firing_assessment": {
                "should_fire": True,
                "why_this_skill_fired": [
                    f"The scenario directly resembles `{primary_anchor.get('anchor_id', skill_id)}`.",
                    f"The neighboring evidence in `{secondary_anchor.get('anchor_id', skill_id)}` keeps the boundary specific.",
                ],
            },
            "boundary_check": {
                "status": "pass",
                "notes": [
                    "This is an automated smoke usage review, not a production judgment.",
                    "The scenario still includes concrete evidence and decision context.",
                ],
            },
            "structured_output": {
                "verdict": verdict if isinstance(verdict, str) else "apply",
                "next_action": next_action,
                "evidence_to_check": evidence_to_check,
                "decline_reason": (
                    "Decline if the scenario loses concrete decision context or if disconfirming "
                    "evidence overrides the anchored pattern."
                ),
                "confidence": "medium",
            },
            "analysis_summary": (
                f"The smoke review fired `{skill_id}` because the scenario is anchored to "
                f"the same evidence path as `{primary_anchor.get('anchor_id', skill_id)}`."
            ),
            "quality_assessment": {
                "contract_fit": "strong" if trigger_patterns else "medium",
                "evidence_alignment": [
                    anchor.get("anchor_id")
                    for anchor in source_anchors[:2]
                    if isinstance(anchor, dict) and anchor.get("anchor_id")
                ],
                "caveats": [
                    "Replace this smoke review with real usage evidence before release."
                ],
            },
        }
        (usage_root / f"{skill_id}-smoke.yaml").write_text(
            yaml.safe_dump(usage_doc, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )


def _write_workflow_gateway_usage_reviews(
    *,
    usage_root: Path,
    run_root: Path,
    bundle_root: Path,
    candidate: dict[str, Any],
    source_anchors: list[dict[str, Any]],
    trigger_patterns: list[str],
) -> None:
    candidate_doc = candidate.get("candidate", {})
    gateway = candidate_doc.get("workflow_gateway", {}) if isinstance(candidate_doc, dict) else {}
    routes_to = [
        str(item)
        for item in (gateway.get("routes_to", []) if isinstance(gateway, dict) else [])
        if str(item).strip()
    ]
    skill_path = str(bundle_root / "skills" / "workflow-gateway" / "SKILL.md")
    anchors = [anchor for anchor in source_anchors if isinstance(anchor, dict)]
    if not anchors:
        anchors = [{"anchor_id": "workflow-gateway", "snippet": "workflow gateway routing evidence"}]
    evidence_alignment = [
        str(anchor.get("anchor_id"))
        for anchor in anchors[:3]
        if anchor.get("anchor_id")
    ]
    while len(evidence_alignment) < 3:
        evidence_alignment.append("workflow-gateway-routing-smoke")
    evidence_to_check = _derive_gateway_evidence_to_check(
        anchors=anchors,
        trigger_patterns=trigger_patterns,
        routes_to=routes_to,
    )
    case_specs = [
        {
            "review_case_id": "workflow-gateway-route-primary",
            "scenario": "用户要做需求分析，但不知道应先从业务流程、业务场景还是干系人分析开始。",
            "decision_goal": "Select the first workflow candidate for a concrete requirements-analysis task.",
            "should_fire": True,
            "verdict": "route_to_workflow",
            "selected_workflow_id": _pick_route(routes_to, ["业务场景", "业务流程"], fallback_index=0),
            "next_action": "route_to_selected_workflow_and_open_its_checklist",
            "boundary_status": "pass",
            "analysis_summary": "Gateway should route because the user has a concrete analysis goal but has not selected the workflow entrypoint.",
        },
        {
            "review_case_id": "workflow-gateway-route-by-hint",
            "scenario": "用户说已经有访谈材料，怀疑当前更适合先做干系人分析，但不确定是否应该直接执行。",
            "decision_goal": "Use a workflow hint to choose the closest auditable workflow candidate.",
            "should_fire": True,
            "verdict": "route_to_workflow",
            "selected_workflow_id": _pick_route(routes_to, ["干系人"], fallback_index=1),
            "next_action": "confirm_hint_then_route_to_matching_workflow",
            "boundary_status": "pass",
            "analysis_summary": "Gateway should respect the user hint, verify it against available context, then route rather than rewrite workflow steps.",
        },
        {
            "review_case_id": "workflow-gateway-sequence-two-workflows",
            "scenario": "用户要从零开始梳理一个业务域，需要知道先识别目标还是先拆业务子系统。",
            "decision_goal": "Sequence two workflow candidates without collapsing them into a thick skill.",
            "should_fire": True,
            "verdict": "route_to_workflow",
            "selected_workflow_id": _pick_route(routes_to, ["目标", "业务子系统"], fallback_index=2),
            "next_action": "sequence_workflow_candidates_without_inlining_steps",
            "boundary_status": "pass",
            "analysis_summary": "Gateway can sequence workflow entrypoints while keeping each deterministic checklist in workflow_candidates/.",
        },
        {
            "review_case_id": "workflow-gateway-ask-context",
            "scenario": "用户只说‘帮我分析一下这本需求书’，没有说明业务目标、已有材料或输出约束。",
            "decision_goal": "Decide whether more context is required before selecting a workflow.",
            "should_fire": True,
            "verdict": "ask_clarifying_question",
            "selected_workflow_id": "",
            "next_action": "ask_for_user_goal_available_context_and_candidate_workflow_hint",
            "boundary_status": "pass",
            "analysis_summary": "Gateway should not guess a workflow when the decision goal and context are underspecified.",
        },
        {
            "review_case_id": "workflow-gateway-refuse-agentic",
            "scenario": "用户要求不要流程，直接替他判断整个企业信息化战略应该怎么定。",
            "decision_goal": "Reject use of the thin gateway when the request asks for broad agentic judgment.",
            "should_fire": False,
            "verdict": "defer",
            "selected_workflow_id": "",
            "next_action": "defer_to_judgment_heavy_skill_or_request_new_agentic_candidate",
            "boundary_status": "pass",
            "analysis_summary": "Gateway must preserve the workflow-vs-agentic boundary and refuse to impersonate a thick strategy skill.",
        },
        {
            "review_case_id": "workflow-gateway-do-not-inline",
            "scenario": "用户希望把所有 workflow 步骤合并成一个万能技能，省得看 workflow_candidates。",
            "decision_goal": "Keep deterministic workflow steps outside the gateway skill.",
            "should_fire": False,
            "verdict": "defer",
            "selected_workflow_id": "",
            "next_action": "explain_boundary_and_point_to_workflow_candidates",
            "boundary_status": "pass",
            "analysis_summary": "Gateway may route to workflow artifacts but must not inline deterministic procedures as agentic reasoning.",
        },
    ]
    for spec in case_specs:
        selected = spec["selected_workflow_id"]
        usage_doc = {
            "review_case_id": spec["review_case_id"],
            "generated_run_root": str(run_root),
            "skill_path": skill_path,
            "input_scenario": {
                "scenario": spec["scenario"],
                "decision_goal": spec["decision_goal"],
                "available_workflow_candidates": routes_to[:12],
                "candidate_workflow_hint": selected,
                "current_constraints": [
                    "Preserve deterministic workflow logic under workflow_candidates/.",
                    "Use the gateway only for routing, sequencing, or missing-context clarification.",
                ],
                "disconfirming_evidence": [
                    "Do not route if the user asks for broad judgment rather than a workflow entrypoint.",
                    "Do not inline workflow.yaml steps inside the gateway response.",
                ],
            },
            "firing_assessment": {
                "should_fire": spec["should_fire"],
                "why_this_skill_fired": [
                    "The request is about selecting, sequencing, or rejecting workflow candidates.",
                    "The gateway preserves workflow-vs-agentic boundary by routing rather than rewriting steps.",
                ],
            },
            "boundary_check": {
                "status": spec["boundary_status"],
                "notes": [
                    "Gateway output remains a router decision, not workflow execution.",
                    "workflow_candidates/ remains the source of deterministic steps.",
                ],
            },
            "structured_output": {
                "verdict": spec["verdict"],
                "selected_workflow_id": selected,
                "routing_reason": spec["analysis_summary"],
                "missing_context": [] if spec["verdict"] != "ask_clarifying_question" else [
                    "user_goal",
                    "available_context",
                    "expected_output",
                ],
                "next_action": spec["next_action"],
                "evidence_to_check": evidence_to_check,
                "decline_reason": "Decline or defer when the request is not a workflow-routing problem.",
            },
            "analysis_summary": spec["analysis_summary"],
            "quality_assessment": {
                "contract_fit": "strong",
                "evidence_alignment": evidence_alignment,
                "caveats": [
                    "This is generated routing evidence; replace with real user routing logs before publication.",
                ],
            },
        }
        (usage_root / f"{spec['review_case_id']}.yaml").write_text(
            yaml.safe_dump(usage_doc, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )


def _derive_gateway_evidence_to_check(
    *,
    anchors: list[dict[str, Any]],
    trigger_patterns: list[str],
    routes_to: list[str],
) -> list[str]:
    evidence_items = []
    for anchor in anchors[:3]:
        anchor_id = anchor.get("anchor_id") or "workflow-gateway-anchor"
        snippet = _compact_snippet(anchor.get("snippet", ""))
        evidence_items.append(f"`{anchor_id}`: {snippet}" if snippet else f"`{anchor_id}`")
    if trigger_patterns:
        evidence_items.append(f"Gateway trigger still satisfied: `{trigger_patterns[0]}`")
    if routes_to:
        evidence_items.append("Available workflow candidates: " + ", ".join(routes_to[:6]))
    return evidence_items


def _pick_route(routes_to: list[str], keywords: list[str], *, fallback_index: int) -> str:
    for keyword in keywords:
        for route in routes_to:
            if keyword in route:
                return route
    if not routes_to:
        return ""
    return routes_to[min(fallback_index, len(routes_to) - 1)]


def _derive_specific_next_action(
    *,
    skill_id: str,
    verdict: str,
    primary_anchor: dict[str, Any],
    secondary_anchor: dict[str, Any],
) -> str:
    primary_fragment = _smoke_action_fragment(primary_anchor, fallback=skill_id)
    secondary_fragment = _smoke_action_fragment(secondary_anchor, fallback=f"{skill_id}_boundary")
    normalized_verdict = verdict.strip().lower()

    if normalized_verdict == "do_not_apply":
        return f"test_{primary_fragment}_against_{secondary_fragment}_disconfirming_evidence"
    if normalized_verdict == "defer":
        return f"resolve_{secondary_fragment}_before_applying_{primary_fragment}"
    return f"verify_{primary_fragment}_evidence_and_{secondary_fragment}_boundary"


def _derive_smoke_evidence_to_check(
    *,
    primary_anchor: dict[str, Any],
    secondary_anchor: dict[str, Any],
    trigger_patterns: list[str],
) -> list[str]:
    evidence_items: list[str] = []
    for anchor in (primary_anchor, secondary_anchor):
        if not isinstance(anchor, dict):
            continue
        anchor_id = anchor.get("anchor_id")
        snippet = _compact_snippet(anchor.get("snippet", ""))
        if anchor_id:
            detail = f"`{anchor_id}`"
            if snippet:
                detail += f": {snippet}"
            evidence_items.append(detail)
    for pattern in trigger_patterns[:1]:
        evidence_items.append(f"Trigger still satisfied: `{pattern}`")
    return evidence_items or ["Re-check the anchored scenario before applying the draft."]


def _smoke_action_fragment(anchor: dict[str, Any], *, fallback: str) -> str:
    if not isinstance(anchor, dict):
        return _normalize_smoke_symbol(fallback)
    raw = anchor.get("anchor_id") or anchor.get("label") or anchor.get("snippet") or fallback
    return _normalize_smoke_symbol(str(raw))


def _normalize_smoke_symbol(raw: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", raw.lower()).strip("_")
    return normalized or "anchored_evidence"


def _compact_snippet(raw: str, *, limit: int = 96) -> str:
    text = " ".join(str(raw).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."
