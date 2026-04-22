#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from kiu_validator.core import validate_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a KiU bundle.")
    parser.add_argument("bundle_path", help="Primary bundle path")
    parser.add_argument(
        "--merge-with",
        action="append",
        default=[],
        dest="merge_with",
        help="Additional bundle path to merge for cross-bundle external relation checks",
    )
    args = parser.parse_args()

    report = validate_bundle(args.bundle_path, merge_with=args.merge_with)
    if report["errors"]:
        print("INVALID")
        print(json.dumps(report["errors"], ensure_ascii=False, indent=2))
        return 1

    payload = {
        "bundle_version": report["manifest"]["bundle_version"],
        "skills": len(report["skills"]),
        "graph": report["graph"],
        "shared_assets": report["shared_assets"],
    }
    if report.get("merged_graph"):
        payload["merged_graph"] = report["merged_graph"]
    print("VALID " + json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
