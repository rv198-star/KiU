#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from kiu_graph.merge import merge_bundle_graphs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Merge KiU bundle graphs into a single namespaced graph document."
    )
    parser.add_argument("bundle_paths", nargs="+", help="Bundle paths to merge")
    parser.add_argument(
        "--output",
        help="Optional path to write merged_graph.json. Defaults to stdout.",
    )
    args = parser.parse_args()

    merged_graph = merge_bundle_graphs(args.bundle_paths)
    payload = json.dumps(merged_graph, ensure_ascii=False, indent=2) + "\n"

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
