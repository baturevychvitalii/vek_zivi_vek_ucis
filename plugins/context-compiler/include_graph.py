#!/usr/bin/env python3
"""
Shared #include graph traversal for the context-compiler plugin.

Provides resolve_include_path and collect_inputs — used by both
preprocess.py (text assembly) and compiled-is-fresh.py (freshness check).
"""
from pathlib import Path


def resolve_include_path(path_str: str, from_file: Path, project_root: Path) -> Path:
    if path_str.startswith("."):
        return (from_file.parent / path_str).resolve()
    return (project_root / path_str).resolve()


def collect_inputs(entry: Path, project_root: Path, seen: set[Path]) -> list[Path]:
    """Return all files reachable from entry via #include, in DFS order."""
    resolved = entry.resolve()
    if resolved in seen or not resolved.exists():
        return []
    seen.add(resolved)
    results = [resolved]
    for line in resolved.read_text().splitlines():
        bare = line.rstrip("\r\n")
        if bare.startswith("#include "):
            path_str = bare[len("#include "):].strip()
            child = resolve_include_path(path_str, resolved, project_root)
            results.extend(collect_inputs(child, project_root, seen))
    return results


def _main() -> None:
    """CLI: list all transitive #include inputs of an entry file, one per line.

    First line is the entry file itself; the rest are its dependencies in DFS
    order. Paths are printed project-root-relative when possible. Used by the
    propagate skill to discover which source layers compose a compiled file.
    """
    import sys

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <entry-file>", file=sys.stderr)
        sys.exit(2)

    entry = Path(sys.argv[1])
    project_root = Path.cwd()

    if not entry.exists():
        print(f"entry file not found: {entry}", file=sys.stderr)
        sys.exit(1)

    for f in collect_inputs(entry, project_root, set()):
        try:
            print(f.relative_to(project_root))
        except ValueError:
            print(f)


if __name__ == "__main__":
    _main()
