#!/usr/bin/env python3
"""
Check whether the compiled output for a source file is up-to-date.

Exit 0 if <stem>.compiled.md exists and is newer than all transitive #include inputs.
Exit 1 otherwise.

Usage: python3 .claude/plugins/context-compiler/compiled-is-fresh.py <source-file.md>
"""
import sys
from pathlib import Path


def resolve_include_path(path_str: str, from_file: Path, project_root: Path) -> Path:
    if path_str.startswith("."):
        return (from_file.parent / path_str).resolve()
    return (project_root / path_str).resolve()


def collect_inputs(entry: Path, project_root: Path, seen: set[Path]) -> list[Path]:
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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <source-file.md>", file=sys.stderr)
        sys.exit(2)

    source = Path(sys.argv[1])
    compiled = source.parent / f"{source.stem}.compiled.md"
    project_root = Path.cwd()

    if not source.exists():
        print(f"source file not found: {source}", file=sys.stderr)
        sys.exit(1)

    if not compiled.exists():
        print(f"compiled output not found: {compiled}")
        sys.exit(1)

    compiled_mtime = compiled.stat().st_mtime
    inputs = collect_inputs(source, project_root, set())

    for f in inputs:
        if f.stat().st_mtime > compiled_mtime:
            print(f"stale: {f.name} is newer")
            sys.exit(1)

    print("up-to-date")
    sys.exit(0)
