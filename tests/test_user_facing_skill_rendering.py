from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from kiu_pipeline.draft import build_candidate_skill_markdown
from kiu_pipeline.models import CandidateSeed


class UserFacingSkillRenderingTests(unittest.TestCase):
    def test_rationale_renders_explicit_mechanism_chain_and_prioritizes_mechanism_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            source = root / "sources" / "book.md"
            source.parent.mkdir(parents=True)
            source.write_text(
                "\n".join(
                    [
                        "序言只说明人物世系与背景。",
                        "团队在没有现场调查时直接按模板定方案，导致关键用户流程被遗漏。后来负责人先访谈一线角色，识别业务约束，再调整系统边界，返工风险下降。",
                    ]
                ),
                encoding="utf-8",
            )

            source_bundle = SimpleNamespace(
                root=root,
                manifest={"bundle_id": "mechanism-fixture", "graph": {"graph_hash": "hash"}},
                graph_doc={
                    "nodes": [
                        {
                            "id": "n-preface",
                            "label": "Preface genealogy",
                            "source_file": "sources/book.md",
                            "source_location": {"line_start": 1, "line_end": 1},
                        },
                        {
                            "id": "n-mechanism",
                            "label": "Investigation prevents rework",
                            "source_file": "sources/book.md",
                            "source_location": {"line_start": 2, "line_end": 2},
                        },
                    ]
                },
            )

            seed = CandidateSeed(
                candidate_id="no-investigation-no-decision",
                candidate_kind="general_agentic",
                primary_node_id="n-preface",
                supporting_node_ids=["n-mechanism"],
                supporting_edge_ids=[],
                community_ids=[],
                gold_match_hint=None,
                source_skill=None,
                score=90,
                metadata={"disposition": "skill_candidate"},
                seed_content={
                    "title": "No Investigation No Decision",
                    "summary": "Decide whether the user must investigate before acting.",
                },
            )

            markdown = build_candidate_skill_markdown(
                source_bundle=source_bundle,
                seed=seed,
                bundle_version="0.2.0",
                skill_revision=1,
            )

        self.assertIn("Mechanism chain", markdown)
        self.assertIn("source anchor -> mechanism observed -> transferable judgment -> user trigger -> anti-misuse boundary", markdown)
        self.assertLess(markdown.index("Investigation prevents rework"), markdown.index("Preface genealogy"))

    def test_workflow_gateway_markdown_declares_thin_router_not_thick_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "sources").mkdir(parents=True)

            source_bundle = SimpleNamespace(
                root=root,
                manifest={"bundle_id": "gateway-fixture", "graph": {"graph_hash": "hash"}},
                graph_doc={"nodes": []},
            )

            seed = CandidateSeed(
                candidate_id="workflow-gateway",
                candidate_kind="workflow_gateway",
                primary_node_id="n1",
                supporting_node_ids=[],
                supporting_edge_ids=[],
                community_ids=[],
                gold_match_hint=None,
                source_skill=None,
                score=80,
                metadata={"disposition": "skill_candidate"},
                seed_content={
                    "title": "Workflow Gateway",
                    "rationale": "Route to workflow candidates without inlining deterministic steps.",
                },
            )

            markdown = build_candidate_skill_markdown(
                source_bundle=source_bundle,
                seed=seed,
                bundle_version="0.2.0",
                skill_revision=1,
            )

        self.assertIn("thin workflow router", markdown.lower())
        self.assertIn("not a thick judgment skill", markdown.lower())


if __name__ == "__main__":
    unittest.main()
