from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from .contracts import identify_semantic_family
from .models import CandidateSeed, SourceBundle


DISTILLATION_SCHEMA_VERSION = "kiu.graph-to-skill-distillation/v0.1"

FAMILY_ACTION_HINTS: dict[str, dict[str, list[str] | str]] = {
    "circle-of-competence": {
        "trigger_signals": [
            "不熟悉领域",
            "我应该差不多能搞明白",
            "Web3 或 AI 新领域",
            "底层技术搞不懂",
            "自媒体变现说不清",
            "餐饮连锁或跨界项目",
        ],
        "action": "先做能力边界测试：列出 missing_knowledge、判断 in_circle / edge_of_circle / outside_circle，再给 study_more 或 decline。",
    },
    "invert-the-problem": {
        "trigger_signals": [
            "方案太乐观",
            "最坏情况",
            "失败路径",
            "血本无归",
            "pre-mortem",
            "只看到机会没看到威胁",
            "创业、上市计划、市场扩张或投资决策",
        ],
        "action": "把目标翻成 failure map：列 failure_modes、avoid_rules、first_preventive_action，并决定 full_inversion / partial_review / defer。",
    },
    "bias-self-audit": {
        "trigger_signals": [
            "不可能错",
            "反面意见不想听",
            "反面证据或反驳",
            "团队都同意",
            "支持我观点的数据",
            "确认偏见、社会认同、过度自信",
            "完美投资逻辑或强 thesis",
        ],
        "action": "先写 thesis，再命名 triggered_biases，指定 strongest counter-evidence，最后给 mitigation_actions 和 next_action。",
    },
    "value-assessment": {
        "trigger_signals": [
            "价格合理吗",
            "安全边际够不够",
            "市盈率和品牌质量",
            "市场恐慌后的错杀",
            "护城河、提价和定价权",
            "天使轮或私有生意值不值得投",
        ],
        "action": "先判断 value_anchor 是否成立，再看 price_or_valuation 是否脱离 business economics，最后 handoff 到 sizing 或 decline。",
    },
    "margin-of-safety-sizing": {
        "trigger_signals": [
            "仓位多大",
            "安全边际够不够",
            "下行空间和流动性",
            "集中下注",
            "panic creates mispricing",
            "private business or angel check",
        ],
        "action": "先确认 downside_range、liquidity_profile 和 entry_price，再给 sizing_band、constraints、next_action 或 refuse。",
    },
    "opportunity-cost-of-the-next-best-idea": {
        "trigger_signals": [
            "下一个最好机会",
            "把钱放在这个项目还是另一个项目",
            "机会成本",
            "错过 Google 这类高质量机会",
            "切换资本配置",
        ],
        "action": "先写 next_best_alternative，再比较 expected_value_delta、irreversibility 和 learning_value，最后给 switch / keep / defer。",
    },
}


def augment_scenario_families(
    *,
    source_bundle: SourceBundle,
    seed: CandidateSeed,
    scenario_families: dict[str, Any] | None,
) -> dict[str, Any]:
    augmented = deepcopy(scenario_families) if isinstance(scenario_families, dict) else {}
    for bucket in ("should_trigger", "should_not_trigger", "edge_case", "refusal"):
        items = augmented.get(bucket, [])
        augmented[bucket] = items if isinstance(items, list) else []

    contract = build_distillation_contract(source_bundle=source_bundle, seed=seed)
    hints = _family_hints(seed)

    for edge in contract["inferred_trigger_expansions"]:
        _append_unique_scenario(
            augmented,
            "should_trigger",
            {
                "scenario_id": f"graph-inferred-link-{edge['id']}",
                "summary": (
                    f"Graph-to-skill distillation: `INFERRED` edge `{edge['id']}` expands trigger language "
                    f"only when a live decision links `{edge['from_label']}` and `{edge['to_label']}`."
                ),
                "prompt_signals": _merge_signals(
                    [edge["from_label"], edge["to_label"], edge.get("snippet", "")],
                    hints.get("trigger_signals", []),
                ),
                "boundary_reason": (
                    "This relation is INFERRED, so it can widen trigger recall only with concrete decision context, "
                    "explicit source evidence, and the existing do_not_fire_when boundary still active."
                ),
                "next_action_shape": _action_with_source(edge, hints),
                "anchor_refs": [edge["id"]],
                "distillation_role": "trigger_expansion",
                "extraction_kind": "INFERRED",
                "source_location": edge["source_location"],
                "graph_navigation": contract["graph_navigation"],
            },
        )

    for item in contract["ambiguous_boundary_probes"]:
        _append_unique_scenario(
            augmented,
            "edge_case",
            {
                "scenario_id": f"graph-ambiguous-boundary-{item['id']}",
                "summary": (
                    f"Graph-to-skill distillation: `AMBIGUOUS` signal `{item['id']}` is a boundary probe, "
                    "not a permission to fire broadly."
                ),
                "prompt_signals": _merge_signals(
                    [item.get("label", ""), item.get("snippet", "")],
                    hints.get("trigger_signals", []),
                ),
                "boundary_reason": (
                    "Because this graph signal is AMBIGUOUS, the skill should use partial_review or defer "
                    "unless live decision context, source evidence, and disconfirming evidence are explicit."
                ),
                "next_action_shape": (
                    f"Check source_location `{item['source_location']}`, name the boundary uncertainty, "
                    "and either narrow the output or decline with a concrete decline_reason."
                ),
                "anchor_refs": [item["id"]],
                "distillation_role": "boundary_probe",
                "extraction_kind": "AMBIGUOUS",
                "source_location": item["source_location"],
                "graph_navigation": contract["graph_navigation"],
            },
        )
    return augmented


def build_distillation_contract(*, source_bundle: SourceBundle, seed: CandidateSeed) -> dict[str, Any]:
    graph_signals = _collect_graph_signals(source_bundle=source_bundle, seed=seed)
    hints = _family_hints(seed)
    navigation = _collect_graph_navigation(source_bundle=source_bundle, seed=seed)
    action = str(hints.get("action") or "Use graph evidence to choose apply / defer / do_not_apply with explicit evidence_to_check.")

    inferred = [
        {
            **edge,
            "trigger_policy": "expand_trigger_only_with_live_decision_context",
            "action_language": action,
        }
        for edge in graph_signals["inferred_edges"]
    ]
    ambiguous = [
        {
            **item,
            "boundary_policy": "turn_into_edge_case_or_refusal_boundary",
            "action_language": "name_uncertainty_then_narrow_or_decline",
        }
        for item in [*graph_signals["ambiguous_nodes"], *graph_signals["ambiguous_edges"]]
    ]

    return {
        "schema_version": DISTILLATION_SCHEMA_VERSION,
        "candidate_id": seed.candidate_id,
        "source_graph_hash": source_bundle.manifest.get("graph", {}).get("graph_hash"),
        "source_graph_version": source_bundle.manifest.get("graph", {}).get("graph_version"),
        "rules": [
            "INFERRED graph edges may expand trigger language but must not override boundary rules.",
            "AMBIGUOUS graph nodes or edges must become edge-case/refusal probes, not broad triggers.",
            "source_location must be translated into concrete next-action language, not left as metadata only.",
            "GRAPH_REPORT navigation may guide related-skill handoff but is not independent evidence.",
        ],
        "inferred_trigger_expansions": inferred,
        "ambiguous_boundary_probes": ambiguous,
        "source_action_transfer": {
            "family": identify_semantic_family(seed.candidate_id),
            "action_language": action,
            "requires_source_location": True,
        },
        "graph_navigation": navigation,
    }


def build_distillation_note(*, source_bundle: SourceBundle, seed: CandidateSeed) -> str:
    contract = build_distillation_contract(source_bundle=source_bundle, seed=seed)
    parts: list[str] = []
    inferred = contract["inferred_trigger_expansions"]
    ambiguous = contract["ambiguous_boundary_probes"]
    if not inferred and not ambiguous:
        return ""
    if inferred:
        edge_bits = [
            f"`{edge['id']}` (`{edge['from_label']}` -> `{edge['to_label']}`, source_location `{edge['source_location']}`)"
            for edge in inferred[:3]
        ]
        parts.append(
            "Graph-to-skill distillation: `INFERRED` graph links "
            + ", ".join(edge_bits)
            + " are rendered as bounded trigger expansion, never as standalone proof."
        )
    if ambiguous:
        boundary_bits = [
            f"`{item['id']}` at source_location `{item['source_location']}`"
            for item in ambiguous[:3]
        ]
        parts.append(
            "Graph-to-skill distillation: `AMBIGUOUS` signals "
            + ", ".join(boundary_bits)
            + " are rendered as edge_case/refusal boundaries before any broad firing."
        )
    navigation = contract.get("graph_navigation", {})
    communities = navigation.get("communities", []) if isinstance(navigation, dict) else []
    if communities:
        labels = ", ".join(
            f"`{item['community_id']}`/{item['label']}" for item in communities[:2]
        )
        parts.append(
            f"Graph navigation: `GRAPH_REPORT.md` places this candidate near {labels}; use this for related-skill handoff, not as independent evidence."
        )
    action = contract.get("source_action_transfer", {}).get("action_language")
    if action:
        parts.append(f"Action-language transfer: {action}")
    return "\n\n".join(parts)


def _collect_graph_signals(*, source_bundle: SourceBundle, seed: CandidateSeed) -> dict[str, list[dict[str, str]]]:
    nodes = {
        node["id"]: node
        for node in source_bundle.graph_doc.get("nodes", [])
        if isinstance(node, dict) and node.get("id")
    }
    edges = {
        edge["id"]: edge
        for edge in source_bundle.graph_doc.get("edges", [])
        if isinstance(edge, dict) and edge.get("id")
    }
    candidate_node_ids = [seed.primary_node_id, *seed.supporting_node_ids]
    candidate_edge_ids = list(seed.supporting_edge_ids)
    inferred_edges: list[dict[str, str]] = []
    ambiguous_edges: list[dict[str, str]] = []
    ambiguous_nodes: list[dict[str, str]] = []

    for edge_id in candidate_edge_ids:
        edge = edges.get(edge_id, {})
        kind = edge.get("extraction_kind")
        if kind not in {"INFERRED", "AMBIGUOUS"}:
            continue
        from_node = nodes.get(edge.get("from"), {})
        to_node = nodes.get(edge.get("to"), {})
        descriptor = {
            "id": edge_id,
            "label": str(edge.get("type") or edge_id),
            "from_label": str(from_node.get("label") or edge.get("from") or ""),
            "to_label": str(to_node.get("label") or edge.get("to") or ""),
            "source_file": str(edge.get("source_file") or ""),
            "source_location": _format_source_location(edge),
            "snippet": _read_snippet(source_bundle=source_bundle, entity=edge),
            "extraction_kind": str(kind),
        }
        if kind == "INFERRED":
            inferred_edges.append(descriptor)
        else:
            ambiguous_edges.append(descriptor)

    for node_id in candidate_node_ids:
        node = nodes.get(node_id, {})
        if node.get("extraction_kind") != "AMBIGUOUS":
            continue
        ambiguous_nodes.append(
            {
                "id": node_id,
                "label": str(node.get("label") or node_id),
                "source_file": str(node.get("source_file") or ""),
                "source_location": _format_source_location(node),
                "snippet": _read_snippet(source_bundle=source_bundle, entity=node),
                "extraction_kind": "AMBIGUOUS",
            }
        )
    return {
        "inferred_edges": inferred_edges,
        "ambiguous_edges": ambiguous_edges,
        "ambiguous_nodes": ambiguous_nodes,
    }


def _collect_graph_navigation(*, source_bundle: SourceBundle, seed: CandidateSeed) -> dict[str, Any]:
    nodes = {
        node.get("id"): node
        for node in source_bundle.graph_doc.get("nodes", [])
        if isinstance(node, dict) and node.get("id")
    }
    communities_by_id = {
        community.get("id"): community
        for community in source_bundle.graph_doc.get("communities", [])
        if isinstance(community, dict) and community.get("id")
    }
    communities: list[dict[str, Any]] = []
    for community_id in seed.community_ids:
        community = communities_by_id.get(community_id, {})
        node_ids = [str(node_id) for node_id in community.get("node_ids", [])]
        top_node_id = seed.primary_node_id if seed.primary_node_id in node_ids else (node_ids[0] if node_ids else "")
        top_node = nodes.get(top_node_id, {})
        communities.append(
            {
                "community_id": community_id,
                "label": str(community.get("label") or community_id),
                "top_node_id": top_node_id,
                "top_node_label": str(top_node.get("label") or top_node_id),
                "node_count": len(node_ids),
            }
        )
    return {
        "graph_report": "GRAPH_REPORT.md",
        "communities": communities,
        "suggested_questions": _read_graph_report_questions(source_bundle.root / "GRAPH_REPORT.md"),
    }


def _append_unique_scenario(doc: dict[str, Any], bucket: str, scenario: dict[str, Any]) -> None:
    items = doc.setdefault(bucket, [])
    if not isinstance(items, list):
        items = []
        doc[bucket] = items
    scenario_id = scenario.get("scenario_id")
    if any(isinstance(item, dict) and item.get("scenario_id") == scenario_id for item in items):
        return
    items.append(scenario)


def _merge_signals(primary: list[str], secondary: Any) -> list[str]:
    signals: list[str] = []
    for value in [*primary, *(secondary if isinstance(secondary, list) else [])]:
        text = " ".join(str(value or "").split())
        if not text:
            continue
        if len(text) > 80:
            text = text[:77].rstrip() + "..."
        if text not in signals:
            signals.append(text)
    return signals[:8]


def _family_hints(seed: CandidateSeed) -> dict[str, list[str] | str]:
    family = identify_semantic_family(seed.candidate_id)
    return FAMILY_ACTION_HINTS.get(family, FAMILY_ACTION_HINTS.get(seed.candidate_id, {}))


def _action_with_source(edge: dict[str, str], hints: dict[str, list[str] | str]) -> str:
    action = str(hints.get("action") or "Use the inferred relation to choose apply / defer / do_not_apply with explicit evidence_to_check.")
    return f"{action} Evidence check: verify source_location `{edge['source_location']}` before expanding the trigger."


def _format_source_location(entity: dict[str, Any]) -> str:
    location = entity.get("source_location")
    source_file = str(entity.get("source_file") or "<missing-source>")
    if not isinstance(location, dict):
        return source_file
    return f"{source_file}:{location.get('line_start', '?')}-{location.get('line_end', '?')}"


def _read_snippet(*, source_bundle: SourceBundle, entity: dict[str, Any]) -> str:
    relative_path = entity.get("source_file")
    if not isinstance(relative_path, str) or not relative_path:
        return ""
    location = entity.get("source_location")
    line_start = 1
    line_end = 1
    if isinstance(location, dict):
        line_start = int(location.get("line_start") or 1)
        line_end = int(location.get("line_end") or line_start)
    path = source_bundle.root / relative_path
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8").splitlines()
    excerpt = " ".join(line.strip() for line in lines[line_start - 1 : line_end] if line.strip())
    return excerpt[:180] if len(excerpt) > 180 else excerpt


def _read_graph_report_questions(path: Any) -> list[str]:
    path = getattr(path, "resolve", lambda: path)()
    if not hasattr(path, "exists") or not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    questions: list[str] = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped == "## Suggested Questions":
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if in_section:
            match = re.match(r"^\d+\.\s+(.*)$", stripped)
            if match:
                questions.append(match.group(1))
    return questions[:5]
