from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


PROVENANCE_SCHEMA_VERSION = "kiu.pipeline-provenance/v0.1"


def build_raw_book_cold_start_provenance(
    *,
    input_path: str | Path,
    source_bundle_root: str | Path,
    run_root: str | Path,
    source_chunks_path: str | Path,
    extraction_result_path: str | Path,
    graph_path: str | Path,
    deterministic_pass: str,
) -> dict[str, Any]:
    source_bundle_root = Path(source_bundle_root)
    manifest = _load_yaml(source_bundle_root / "manifest.yaml")
    skills = manifest.get("skills", []) if isinstance(manifest.get("skills"), list) else []
    return {
        "schema_version": PROVENANCE_SCHEMA_VERSION,
        "pipeline_mode": "raw_book_no_seed_cold_start",
        "raw_book_no_seed_cold_start": len(skills) == 0,
        "input_kind": "raw_markdown_book",
        "source_input_path": str(Path(input_path)),
        "source_bundle_root": str(source_bundle_root),
        "run_root": str(Path(run_root)),
        "source_bundle_id": manifest.get("bundle_id"),
        "source_bundle_skill_count": len(skills),
        "uses_existing_source_skills": len(skills) > 0,
        "uses_reference_pack_as_generation_input": False,
        "manual_generated_artifact_patch_allowed": False,
        "artifact_paths": {
            "source_chunks": str(Path(source_chunks_path)),
            "extraction_result": str(Path(extraction_result_path)),
            "graph": str(Path(graph_path)),
        },
        "extraction": {
            "deterministic_pass": deterministic_pass,
        },
        "claim_boundary": (
            "This run may be claimed as raw-book no-seed cold start only if "
            "raw_book_no_seed_cold_start is true and source_bundle_skill_count is 0."
        ),
    }


def build_source_bundle_regeneration_provenance(
    *,
    source_bundle_root: str | Path,
    run_root: str | Path,
    entrypoint: str,
) -> dict[str, Any]:
    source_bundle_root = Path(source_bundle_root)
    manifest = _load_yaml(source_bundle_root / "manifest.yaml")
    skills = manifest.get("skills", []) if isinstance(manifest.get("skills"), list) else []
    return {
        "schema_version": PROVENANCE_SCHEMA_VERSION,
        "pipeline_mode": "source_bundle_regeneration",
        "raw_book_no_seed_cold_start": False,
        "input_kind": "source_bundle",
        "source_bundle_root": str(source_bundle_root),
        "run_root": str(Path(run_root)),
        "source_bundle_id": manifest.get("bundle_id"),
        "source_bundle_skill_count": len(skills),
        "uses_existing_source_skills": len(skills) > 0,
        "uses_reference_pack_as_generation_input": False,
        "manual_generated_artifact_patch_allowed": False,
        "entrypoint": entrypoint,
        "claim_boundary": (
            "This run regenerates candidates from an existing source bundle. It must not "
            "be described as raw-book no-seed cold start."
        ),
    }


def write_pipeline_provenance(run_root: str | Path, doc: dict[str, Any]) -> Path:
    path = Path(run_root) / "reports" / "pipeline-provenance.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def load_pipeline_provenance(run_root: str | Path) -> dict[str, Any]:
    path = Path(run_root) / "reports" / "pipeline-provenance.json"
    if not path.exists():
        return {
            "schema_version": PROVENANCE_SCHEMA_VERSION,
            "pipeline_mode": "unknown",
            "raw_book_no_seed_cold_start": False,
            "claim_boundary": "No pipeline-provenance.json was found; this run must not be claimed as cold start.",
        }
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return loaded if isinstance(loaded, dict) else {}
