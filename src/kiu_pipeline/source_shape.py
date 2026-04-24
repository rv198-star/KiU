from __future__ import annotations

from typing import Any


BORROWED_VALUE_TAGS = {
    "biography_heavy",
    "history_heavy",
    "case_heavy",
    "narrative_case_heavy",
    "argument_strategy_heavy",
    "policy_boundary_heavy",
    "action_program_heavy",
}


def classify_source_shape(source_chunks_doc: dict[str, Any]) -> dict[str, Any]:
    chunks = [
        chunk
        for chunk in source_chunks_doc.get("chunks", [])
        if isinstance(chunk, dict) and isinstance(chunk.get("chunk_text"), str)
    ]
    source_files = source_chunks_doc.get("source_files")
    source_file_count = len(source_files) if isinstance(source_files, list) else 1
    corpus = "\n".join(str(chunk.get("chunk_text", "")) for chunk in chunks)
    scores = {
        "biography_heavy": _keyword_score(corpus, ("生", "卒", "传", "人物", "先生", "同志", "经历", "事迹")),
        "history_heavy": _keyword_score(corpus, ("战争", "时期", "历史", "国", "军", "敌", "年", "时局", "形势")),
        "case_heavy": _keyword_score(corpus, ("例如", "如", "案例", "事变", "战例", "经验", "教训", "结果")),
        "narrative_case_heavy": _keyword_score(corpus, ("于是", "遂", "乃", "卒", "故", "因", "胜", "败", "亡", "祸")),
        "argument_strategy_heavy": _keyword_score(corpus, ("策略", "战略", "方针", "政策", "路线", "任务", "办法", "原则")),
        "policy_boundary_heavy": _keyword_score(corpus, ("必须", "不要", "不能", "反对", "纠正", "错误", "左", "右", "边界")),
        "action_program_heavy": _keyword_score(corpus, ("组织", "动员", "开展", "集中", "实行", "执行", "领导", "工作", "方法")),
    }
    threshold = max(3, min(12, max(len(chunks) // 8, 3)))
    tags = sorted(tag for tag, score in scores.items() if score >= threshold)
    borrowed_value_ready = any(tag in BORROWED_VALUE_TAGS for tag in tags)
    return {
        "schema_version": "kiu.source-shape/v0.1",
        "source_file_count": source_file_count,
        "chunk_count": len(chunks),
        "tags": tags,
        "scores": scores,
        "borrowed_value_strategy": "borrowed_value_maximization" if borrowed_value_ready else None,
        "graph_layer_policy": {
            "extract_evidence_even_when_skill_rejects_trigger": True,
            "allowed_evidence_kinds": [
                "summaries",
                "original_text_segments",
                "factual_entities",
                "biographical_entities",
                "positions_and_claims",
                "chronology",
                "argument_structure",
                "case_mechanisms",
            ],
        },
        "skill_layer_policy": {
            "must_reject_as_trigger": [
                "pure_summary_request",
                "pure_translation_request",
                "fact_lookup_request",
                "biography_intro_request",
                "author_position_query",
                "stance_commentary_without_user_decision",
            ],
        },
    }


def _keyword_score(corpus: str, keywords: tuple[str, ...]) -> int:
    return sum(corpus.count(keyword) for keyword in keywords)
