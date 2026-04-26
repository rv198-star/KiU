from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import yaml

from kiu_pipeline.action_identity import assess_action_skill_identity, build_action_identity_report
from kiu_pipeline.action_identity import derive_semantic_action_slug
from kiu_pipeline.models import CandidateSeed
from kiu_pipeline.render import render_generated_run, should_publish_skill_seed as render_publish_decision


def _seed(
    candidate_id: str,
    *,
    title: str | None = None,
    summary: str = "",
    trigger: str | None = None,
    output: str | None = None,
    boundaries: list[str] | None = None,
    candidate_kind: str = "general_agentic",
    disposition: str = "skill_candidate",
) -> CandidateSeed:
    seed_content = {
        "title": title or candidate_id,
        "summary": summary,
        "trigger": trigger or summary,
        "output": output or summary,
        "boundaries": boundaries or [],
    }
    return CandidateSeed(
        candidate_id=candidate_id,
        candidate_kind=candidate_kind,
        primary_node_id="node-1",
        supporting_node_ids=["node-1", "node-2"],
        supporting_edge_ids=["edge-1"],
        community_ids=["community-1"],
        gold_match_hint=None,
        source_skill=None,
        score=90,
        metadata={"disposition": disposition, "drafting_mode": "deterministic"},
        seed_content=seed_content,
    )


class ActionIdentityTests(unittest.TestCase):
    def test_semantic_action_slug_replaces_financial_section_heading_identity(self) -> None:
        self.assertEqual(
            derive_semantic_action_slug("M3.2 “漂亮 50” 股票？回到股票筛选的问题上来"),
            "price-value-screening-gate",
        )

    def test_agentic_judgment_skill_routes_to_publish_skill(self) -> None:
        assessment = assess_action_skill_identity(
            _seed(
                "solution-to-problem-reframing",
                summary=(
                    "Use when a team is stuck debating a proposed solution. Reframe the decision by "
                    "separating the underlying problem, constraints, tradeoffs, and next action."
                ),
                trigger="When solution debate hides the real problem or tradeoff.",
                output="A problem statement, decision boundary, next action, and disconfirmation check.",
                boundaries=["Do not use for pure summary or mechanical template filling."],
            )
        )

        self.assertEqual(assessment["route"], "publish_skill")
        self.assertGreaterEqual(assessment["action_skill_identity_score"], 0.85)
        self.assertFalse(assessment["container_signals"])

    def test_container_or_exercise_candidate_does_not_route_to_publish_skill(self) -> None:
        for candidate_id in ["关键概念", "练习题", "自主练习", "迷你案例"]:
            with self.subTest(candidate_id=candidate_id):
                assessment = assess_action_skill_identity(
                    _seed(
                        candidate_id,
                        summary="本节整理书中的概念、案例、习题和材料，供读者复习原书内容。",
                        trigger="阅读本章后复习相关概念。",
                        output="概念列表、案例材料或练习题。",
                    )
                )

                self.assertNotEqual(assessment["route"], "publish_skill")
                self.assertLess(assessment["action_skill_identity_score"], 0.85)
                self.assertTrue(assessment["container_signals"])

    def test_workflow_gateway_routes_to_publish_gateway(self) -> None:
        assessment = assess_action_skill_identity(
            _seed(
                "workflow-gateway",
                summary="Select, sequence, or defer deterministic workflow candidates without inlining their checklist steps.",
                trigger="When the user needs to choose among available workflow candidates.",
                output="A route to the correct workflow candidate or a request for missing context.",
                candidate_kind="workflow_gateway",
            )
        )

        self.assertEqual(assessment["route"], "publish_gateway")
        self.assertGreaterEqual(assessment["action_skill_identity_score"], 0.75)

    def test_report_summarizes_route_distribution_and_leaks(self) -> None:
        report = build_action_identity_report(
            [
                _seed(
                    "circle-of-competence",
                    summary="Decide whether a case is inside your competence before acting.",
                    trigger="Use when context or evidence is insufficient and action may exceed competence.",
                    output="A verdict, boundary, next action, and disconfirmation check.",
                    boundaries=["Do not use to force action outside the evidence boundary."],
                ),
                _seed("练习题", summary="本节包含练习题和答案材料。"),
                _seed("workflow-gateway", candidate_kind="workflow_gateway", summary="Route workflow candidates."),
            ],
            published_candidate_ids=["circle-of-competence", "练习题", "workflow-gateway"],
        )

        self.assertEqual(report["schema_version"], "kiu.action-skill-identity/v0.1")
        self.assertEqual(report["candidate_route_distribution"]["publish_skill"], 1)
        self.assertEqual(report["candidate_route_distribution"]["route_evaluation_material"], 1)
        self.assertEqual(report["candidate_route_distribution"]["publish_gateway"], 1)
        self.assertEqual(report["container_candidate_leak_count"], 1)
        self.assertLess(report["publishable_action_skill_ratio"], 1.0)

    def test_generated_run_writes_action_identity_report_and_routes_container_candidate(self) -> None:
        seeds = [
            _seed(
                "circle-of-competence",
                summary="Decide whether a case is inside your competence before acting.",
                trigger="Use when context or evidence is insufficient and action may exceed competence.",
                output="A verdict, boundary, next action, and disconfirmation check.",
                boundaries=["Do not use to force action outside the evidence boundary."],
            ),
            _seed("练习题", summary="本节包含练习题和答案材料。"),
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            source_root = Path(tmp_dir) / "source"
            for relative in ("graph", "traces", "evaluation", "sources"):
                (source_root / relative).mkdir(parents=True)

            class SourceBundleStub:
                root = source_root
                domain = "test"
                manifest = {
                    "bundle_id": "action-identity-fixture",
                    "bundle_version": "0.1",
                    "language": "zh-CN",
                    "graph": {"path": "graph.yaml", "graph_version": "0.1", "graph_hash": "hash"},
                    "shared_assets": {},
                }
                profile = {"profile_version": "test", "max_candidate_skills": 10}
                graph_doc = {"nodes": [], "edges": []}
                skills = {}
                evaluation_cases = []

            run_root = render_generated_run(
                source_bundle=SourceBundleStub(),
                seeds=seeds,
                output_root=Path(tmp_dir),
                run_id="diagnostic-only",
            )
            report = json.loads((run_root / "reports" / "action-skill-identity.json").read_text(encoding="utf-8"))
            manifest = yaml.safe_load((run_root / "bundle" / "manifest.yaml").read_text(encoding="utf-8"))
            routed_route_exists = (
                run_root
                / "routed_source_values"
                / "route_evaluation_material"
                / "练习题"
                / "route.yaml"
            ).exists()

        self.assertEqual(report["container_candidate_leak_count"], 0)
        self.assertEqual(report["candidate_route_distribution"]["route_evaluation_material"], 1)
        self.assertNotIn("练习题", {entry["skill_id"] for entry in manifest["skills"]})
        self.assertTrue(routed_route_exists)

    def test_identity_gate_blocks_container_from_published_skills(self) -> None:
        decision = render_publish_decision(
            _seed("练习题", summary="本节包含练习题和答案材料。")
        )

        self.assertFalse(decision["publish"])
        self.assertEqual(decision["reason"], "action_skill_identity_below_publish_threshold")
        self.assertEqual(decision["route"], "route_evaluation_material")

    def test_identity_gate_keeps_gateway_publishable(self) -> None:
        decision = render_publish_decision(
            _seed(
                "workflow-gateway",
                candidate_kind="workflow_gateway",
                summary="Select or sequence workflow candidates without inlining deterministic steps.",
            )
        )

        self.assertTrue(decision["publish"])
        self.assertEqual(decision["route"], "publish_gateway")

    def test_identity_gate_keeps_workflow_candidates_routable(self) -> None:
        decision = render_publish_decision(
            _seed(
                "workflow-checklist",
                candidate_kind="workflow_script",
                disposition="workflow_script_candidate",
                summary="Run a deterministic checklist when workflow and context certainty are high.",
            )
        )

        self.assertTrue(decision["publish"])
        self.assertEqual(decision["route"], "route_workflow_candidate")

    def test_identity_gate_keeps_judgment_skill_publishable(self) -> None:
        decision = render_publish_decision(
            _seed(
                "historical-analogy-transfer-gate",
                summary="Use when deciding whether a historical analogy can guide a current decision.",
                trigger="When a user wants to borrow a historical case for a live decision.",
                output="Mechanism comparison, transfer verdict, anti-misuse boundary, and next action.",
                boundaries=["Do not use for pure history summary or fact lookup."],
            )
        )

        self.assertTrue(decision["publish"])
        self.assertEqual(decision["route"], "publish_skill")


if __name__ == "__main__":
    unittest.main()
