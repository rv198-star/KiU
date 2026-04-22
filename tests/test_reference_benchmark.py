import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _write_reference_pack(root: Path, skill_slugs: list[str]) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "BOOK_OVERVIEW.md").write_text("# Book Overview\n", encoding="utf-8")
    (root / "INDEX.md").write_text("# Index\n", encoding="utf-8")
    (root / "candidates").mkdir(exist_ok=True)
    (root / "rejected").mkdir(exist_ok=True)
    for slug in skill_slugs:
        skill_dir = root / slug
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    f"name: {slug}",
                    "source_book: Test Reference Book",
                    "source_chapter: Chapter 1",
                    "---",
                    "",
                    f"# {slug}",
                    "",
                    "## R — 原文",
                    "> 引用原文片段。",
                    "",
                    "## E — 可执行步骤",
                    "1. 执行第一步。",
                    "",
                    "## B — 边界",
                    "不要在证据不足时使用。",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    return root


def _write_test_prompts(skill_dir: Path, payload: dict[str, object]) -> None:
    (skill_dir / "test-prompts.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_alignment_file(root: Path) -> Path:
    path = root / "alignment.yaml"
    path.write_text(
        "\n".join(
            [
                "schema_version: kiu.reference-alignment/v0.1",
                "alignment_id: test-alignment",
                "pairs:",
                "  - kiu_skill_id: circle-of-competence",
                "    reference_skill_id: circle-of-competence",
                "    relationship: direct_match",
                "  - kiu_skill_id: invert-the-problem",
                "    reference_skill_id: inversion-thinking",
                "    relationship: close_match",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


class ReferenceBenchmarkCliTests(unittest.TestCase):
    def test_reference_benchmark_cli_emits_bundle_comparison_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            reference_root = _write_reference_pack(
                tmp_root / "reference-poor-charlies",
                ["circle-of-competence", "inversion-thinking", "value-assessment"],
            )
            alignment_path = _write_alignment_file(tmp_root)
            output_path = tmp_root / "benchmark.json"

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "benchmark_reference_pack.py"),
                    "--kiu-bundle",
                    str(ROOT / "bundles" / "poor-charlies-almanack-v0.1"),
                    "--reference-pack",
                    str(reference_root),
                    "--alignment-file",
                    str(alignment_path),
                    "--comparison-scope",
                    "same-source",
                    "--output",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(output_path.read_text(encoding="utf-8"))

            self.assertEqual(payload["comparison"]["scope"], "same-source")
            self.assertEqual(payload["kiu_bundle"]["skill_count"], 5)
            self.assertEqual(payload["reference_pack"]["skill_count"], 3)
            self.assertGreater(
                payload["comparison"]["output_count"]["bundle_throughput_vs_reference"],
                1.0,
            )
            self.assertEqual(
                payload["comparison"]["evidence_traceability"]["kiu_double_anchor_ratio"],
                1.0,
            )
            self.assertTrue(
                payload["comparison"]["workflow_vs_agentic_boundary"]["kiu_explicit_boundary"]
            )
            self.assertEqual(payload["concept_alignment"]["summary"]["matched_pair_count"], 2)
            self.assertGreater(
                payload["concept_alignment"]["summary"]["kiu_average_artifact_score_100"],
                0.0,
            )
            first_pair = payload["concept_alignment"]["matched_pairs"][0]
            self.assertIn("kiu_review", first_pair)
            self.assertIn("reference_review", first_pair)
            self.assertIn("overall_artifact_score_100", first_pair["kiu_review"])
            self.assertIn("overall_artifact_score_100", first_pair["reference_review"])
            self.assertIn("kiu_foundation_retained_100", payload["scorecard"])
            self.assertIn("graphify_core_absorbed_100", payload["scorecard"])
            self.assertIn("cangjie_core_absorbed_100", payload["scorecard"])
            self.assertTrue(output_path.with_suffix(".md").exists())

    def test_reference_benchmark_cli_includes_generated_run_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            output_root = tmp_root / "artifacts"
            reference_root = _write_reference_pack(
                tmp_root / "reference-engineering",
                ["problem-first-analysis", "business-interface-analysis", "constraint-checklist"],
            )

            pipeline = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "run_book_pipeline.py"),
                    "--input",
                    str(ROOT / "examples" / "sources" / "effective-requirements-analysis-source.md"),
                    "--bundle-id",
                    "demo-source-bundle",
                    "--source-id",
                    "effective-requirements-analysis",
                    "--run-id",
                    "reference-benchmark-smoke",
                    "--output-root",
                    str(output_root),
                    "--max-chars",
                    "240",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(pipeline.returncode, 0, pipeline.stdout + pipeline.stderr)
            pipeline_payload = json.loads(pipeline.stdout)

            benchmark_path = tmp_root / "generated-benchmark.json"
            benchmark = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "benchmark_reference_pack.py"),
                    "--kiu-bundle",
                    pipeline_payload["source_bundle_root"],
                    "--run-root",
                    pipeline_payload["run_root"],
                    "--reference-pack",
                    str(reference_root),
                    "--comparison-scope",
                    "structure-only",
                    "--output",
                    str(benchmark_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(benchmark.returncode, 0, benchmark.stdout + benchmark.stderr)

            payload = json.loads(benchmark_path.read_text(encoding="utf-8"))
            self.assertGreaterEqual(payload["generated_run"]["skill_count"], 1)
            self.assertGreaterEqual(
                payload["generated_run"]["workflow_candidate_count"],
                2,
            )
            self.assertTrue(
                payload["comparison"]["workflow_vs_agentic_boundary"]["kiu_boundary_preserved"]
            )
            self.assertGreater(
                payload["comparison"]["real_usage_quality"]["kiu_usage_score_100"],
                0.0,
            )
            self.assertGreater(
                payload["scorecard"]["details"]["cangjie_core_absorbed"]["pipeline_stage_presence_ratio"],
                0.0,
            )
            self.assertGreater(
                payload["scorecard"]["details"]["graphify_core_absorbed"]["tri_state_effectiveness_ratio"],
                0.0,
            )
            self.assertGreater(
                payload["generated_run"]["source_tri_state_effectiveness"]["candidate_coverage_ratio"],
                0.5,
            )
            self.assertGreater(
                payload["comparison"]["output_count"]["generated_throughput_vs_reference"],
                0.0,
            )

    def test_reference_benchmark_cli_emits_same_scenario_usage_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            reference_root = _write_reference_pack(
                tmp_root / "reference-poor-charlies",
                ["circle-of-competence", "inversion-thinking"],
            )
            _write_test_prompts(
                reference_root / "circle-of-competence",
                {
                    "skill": "circle-of-competence",
                    "version": "0.1.0",
                    "test_cases": [
                        {
                            "id": "should-trigger-01",
                            "type": "should_trigger",
                            "prompt": "有个朋友拉我一起投资他的餐饮连锁项目，我之前从来没做过餐饮，但我觉得应该差不多能搞明白。",
                            "expected_behavior": "应激活 circle-of-competence，帮助用户测试自己是否真的理解这门生意，而不是靠模糊自信下注。",
                            "notes": "真实投资判断，不是概念问答。",
                        },
                        {
                            "id": "should-not-trigger-01",
                            "type": "should_not_trigger",
                            "prompt": "能力圈是什么概念？芒格和巴菲特怎么定义它？",
                            "expected_behavior": "不应激活本 skill，因为用户只是在问概念定义，不是在做真实投资判断。",
                            "notes": "关键词命中但属于知识查询。",
                        },
                        {
                            "id": "edge-01",
                            "type": "edge_case",
                            "prompt": "我做了5年产品经理，现在有机会去一个完全不同行业做产品，我想试试看，但怕自己搞不定。",
                            "expected_behavior": "可以激活但应保留边界判断，区分哪些通用能力可迁移，哪些行业知识仍在圈外。",
                            "notes": "部分圈内，部分圈外。",
                        },
                    ],
                    "minimum_pass_rate": 0.8,
                },
            )
            _write_test_prompts(
                reference_root / "inversion-thinking",
                {
                    "skill": "inversion-thinking",
                    "version": "0.1.0",
                    "test_cases": [
                        {
                            "id": "should-trigger-01",
                            "type": "should_trigger",
                            "prompt": "我们只看市场机会，帮我反过来想想这个产品发布会怎么彻底失败。",
                            "expected_behavior": "应激活 inversion-thinking，引导用户从失败路径出发列出致命风险。",
                            "notes": "典型逆向思考触发场景。",
                        },
                        {
                            "id": "should-not-trigger-01",
                            "type": "should_not_trigger",
                            "prompt": "逆向思维是什么意思？给我讲几个历史故事。",
                            "expected_behavior": "不应激活本 skill，因为这是概念解释，不是正在做风险规避式决策。",
                            "notes": "知识查询，不是方法应用。",
                        },
                    ],
                    "minimum_pass_rate": 0.8,
                },
            )
            alignment_path = _write_alignment_file(tmp_root)
            output_path = tmp_root / "benchmark-same-scenario.json"

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "benchmark_reference_pack.py"),
                    "--kiu-bundle",
                    str(ROOT / "bundles" / "poor-charlies-almanack-v0.1"),
                    "--reference-pack",
                    str(reference_root),
                    "--alignment-file",
                    str(alignment_path),
                    "--comparison-scope",
                    "same-source",
                    "--output",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(output_path.read_text(encoding="utf-8"))

            self.assertIn("same_scenario_usage", payload)
            self.assertEqual(payload["same_scenario_usage"]["summary"]["matched_pair_count"], 2)
            self.assertEqual(payload["same_scenario_usage"]["summary"]["scenario_count"], 5)
            self.assertGreater(
                payload["same_scenario_usage"]["summary"]["kiu_average_usage_score_100"],
                0.0,
            )
            self.assertGreater(
                payload["same_scenario_usage"]["summary"]["reference_average_usage_score_100"],
                0.0,
            )
            self.assertGreater(
                payload["comparison"]["real_usage_quality"]["reference_same_scenario_usage_score_100"],
                0.0,
            )
            first_pair = payload["same_scenario_usage"]["matched_pairs"][0]
            self.assertIn("kiu_usage_review", first_pair)
            self.assertIn("reference_usage_review", first_pair)
            self.assertEqual(first_pair["scenario_count"], len(first_pair["cases"]))
            self.assertIn("minimum_pass_rate", first_pair)
            first_case = first_pair["cases"][0]
            self.assertIn("case_id", first_case)
            self.assertIn("type", first_case)
            self.assertIn("kiu_review", first_case)
            self.assertIn("reference_review", first_case)
            self.assertIn("overall_score_100", first_case["kiu_review"])
            self.assertIn("verdict", first_case["reference_review"])


if __name__ == "__main__":
    unittest.main()
