#!/usr/bin/env python3
"""Merge extra vocab/grammar data into the main files and sync to docs/."""

import json
import shutil
from pathlib import Path

DATA = Path(__file__).parent / "data"
DOCS_DATA = Path(__file__).parent / "docs" / "data"


def merge_json(main_file: Path, extra_file: Path):
    """Merge extra entries into main file by category."""
    main = json.loads(main_file.read_text(encoding="utf-8"))
    extra = json.loads(extra_file.read_text(encoding="utf-8"))

    for cat, entries in extra.items():
        if cat in main:
            # Deduplicate by korean field (or pattern for grammar)
            existing = set()
            for e in main[cat]:
                key = e.get("korean") or e.get("pattern") or ""
                existing.add(key)
            for e in entries:
                key = e.get("korean") or e.get("pattern") or ""
                if key not in existing:
                    main[cat].append(e)
                    existing.add(key)
        else:
            main[cat] = entries

    main_file.write_text(json.dumps(main, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Merged {extra_file.name} into {main_file.name}")

    # Count
    total = sum(len(v) for v in main.values())
    for cat, entries in main.items():
        print(f"  {cat}: {len(entries)}")
    print(f"  Total: {total}")


def sync_docs():
    """Copy data files to docs/ for GitHub Pages."""
    DOCS_DATA.mkdir(parents=True, exist_ok=True)
    for f in DATA.glob("*.json"):
        if f.name.endswith("_extra.json"):
            continue
        shutil.copy2(f, DOCS_DATA / f.name)
        print(f"Synced {f.name} to docs/data/")


if __name__ == "__main__":
    vocab_extra = DATA / "vocab_extra.json"
    grammar_extra = DATA / "grammar_extra.json"

    if vocab_extra.exists():
        merge_json(DATA / "vocab.json", vocab_extra)
    if grammar_extra.exists():
        merge_json(DATA / "grammar.json", grammar_extra)

    sync_docs()
    print("Done!")
