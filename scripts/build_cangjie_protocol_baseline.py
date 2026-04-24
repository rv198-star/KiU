#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from kiu_pipeline.cangjie_protocol import build_cangjie_protocol_baseline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build an explicit cangjie RIA-TV++ protocol baseline from raw markdown. "
            "This is benchmark-only and not an official cangjie runtime."
        )
    )
    parser.add_argument("--input", required=True, help="Raw markdown file or directory.")
    parser.add_argument("--output-root", required=True, help="Reference pack output directory.")
    parser.add_argument("--book-title", required=True, help="Book title for reference metadata.")
    parser.add_argument("--author", required=True, help="Book author for reference metadata.")
    parser.add_argument("--source-id", default="source-book", help="Machine-friendly source id.")
    parser.add_argument("--publication-year", default="unknown", help="Publication year label.")
    parser.add_argument("--max-chars", type=int, default=1200, help="Chunk size used by source ingestion.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_cangjie_protocol_baseline(
        input_path=args.input,
        output_root=args.output_root,
        book_title=args.book_title,
        author=args.author,
        source_id=args.source_id,
        publication_year=args.publication_year,
        max_chars=args.max_chars,
    )
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
