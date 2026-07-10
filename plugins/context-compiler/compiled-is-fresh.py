#!/usr/bin/env python3
"""
Check whether the compiled output for a source file is up-to-date.

Exit 0 and print FRESH or STALE to stdout — the caller branches on that token, not
the exit code. Exit non-zero (with stderr) only for a genuine error: bad usage,
missing source, or a broken #include.

Usage: python3 compiled-is-fresh.py <source-file.md>
"""
import sys
from pathlib import Path
from include_graph import collect_inputs


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"USAGE_ERROR: {sys.argv[0]} <source-file.md>", file=sys.stderr)
        sys.exit(2)

    source = Path(sys.argv[1])
    compiled = source.parent / f"{source.stem}.compiled.md"
    project_root = Path.cwd()

    if not source.exists():
        print(f"SOURCE_NOT_FOUND: {source} — stop and report this.", file=sys.stderr)
        sys.exit(1)

    if not compiled.exists():
        print(f"STALE: {compiled} does not exist yet — proceed to preprocess.")
        sys.exit(0)

    compiled_mtime = compiled.stat().st_mtime
    try:
        inputs = collect_inputs(source, project_root, set())
    except FileNotFoundError as e:
        print(f"BROKEN_INCLUDE: {e} — fix the path before recompiling. Stop and report this.", file=sys.stderr)
        sys.exit(1)

    for f in inputs:
        if f.stat().st_mtime > compiled_mtime:
            print(f"STALE: {f.name} is newer than the compiled output — proceed to preprocess.")
            sys.exit(0)

    print("FRESH — already up-to-date. Stop and report this.")
    sys.exit(0)
