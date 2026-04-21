from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
SHARED_PROFILES_ROOT = REPO_ROOT / "shared_profiles"


def resolve_profile(bundle_path: str | Path) -> dict[str, Any]:
    bundle_root = Path(bundle_path)
    manifest = _load_yaml(bundle_root / "manifest.yaml")
    domain = manifest.get("domain")
    if not domain:
        raise ValueError(f"{bundle_root}: manifest missing required domain")

    bundle_profile = _load_yaml(bundle_root / "automation.yaml")
    inherits = bundle_profile.get("inherits", domain)
    default_profile = _load_yaml(SHARED_PROFILES_ROOT / "default" / "profile.yaml")
    domain_profile_path = SHARED_PROFILES_ROOT / inherits / "profile.yaml"
    if not domain_profile_path.exists():
        raise FileNotFoundError(f"missing domain profile for {inherits}: {domain_profile_path}")
    domain_profile = _load_yaml(domain_profile_path)

    bundle_overrides = dict(bundle_profile)
    bundle_overrides.pop("inherits", None)

    resolved = _deep_merge(default_profile, domain_profile)
    resolved = _deep_merge(resolved, bundle_overrides)
    resolved["domain"] = domain
    resolved["resolved_from"] = ["default", inherits, "bundle"]
    return resolved


def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    return loaded or {}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged
