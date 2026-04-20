#!/usr/bin/env python3
"""
Check whether compiled.md is up-to-date for a deck directory.

Exit 0 if compiled.md exists and is newer than all inheritable-*.md inputs.
Exit 1 otherwise.

Usage: python3 .claude/scripts/compiled-is-fresh.py <deck-dir>
"""
import sys
import os
from pathlib import Path

# Reuse find-inheritables logic inline to avoid subprocess overhead.
def find_inheritables(deck_dir: str) -> list[Path]:
    target = Path(deck_dir).resolve()
    project_root = Path.cwd().resolve()

    ancestors = []
    current = target
    while True:
        ancestors.append(current)
        if current == project_root or current.parent == current:
            break
        current = current.parent

    ancestors.reverse()

    results = []
    for directory in ancestors:
        results.extend(sorted(directory.glob("inheritable-*.md")))
    return results


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <deck-dir>", file=sys.stderr)
        sys.exit(2)

    deck_dir = sys.argv[1]
    compiled = Path(deck_dir) / "compiled.md"

    if not compiled.exists():
        print("compiled.md not found")
        sys.exit(1)

    compiled_mtime = compiled.stat().st_mtime
    inputs = find_inheritables(deck_dir)

    if not inputs:
        print("no inheritable inputs found")
        sys.exit(1)

    for f in inputs:
        if f.stat().st_mtime > compiled_mtime:
            print(f"stale: {f.name} is newer")
            sys.exit(1)

    print("up-to-date")
    sys.exit(0)
