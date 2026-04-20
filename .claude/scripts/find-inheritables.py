#!/usr/bin/env python3
"""
Print the ordered list of inheritable-*.md files for a deck directory.

Usage: python3 .claude/scripts/find-inheritables.py <deck-dir>

Output: one project-root-relative path per line, root-first order.
"""
import sys
import os
from pathlib import Path


def find_inheritables(deck_dir: str) -> list[str]:
    target = Path(deck_dir).resolve()
    project_root = Path.cwd().resolve()

    # Collect ancestor dirs from target up to (but not past) project root,
    # only within the decks/ subtree.
    ancestors = []
    current = target
    while True:
        ancestors.append(current)
        if current == project_root or current.parent == current:
            break
        current = current.parent

    # Reverse so root-side ancestors come first.
    ancestors.reverse()

    results = []
    for directory in ancestors:
        files = sorted(directory.glob("inheritable-*.md"))
        for f in files:
            results.append(str(f.relative_to(project_root)))

    return results


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <deck-dir>", file=sys.stderr)
        sys.exit(2)

    paths = find_inheritables(sys.argv[1])
    for p in paths:
        print(p)
