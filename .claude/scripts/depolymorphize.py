#!/usr/bin/env python3
"""
Concatenate a deck's inheritable-*.md chain into depolymorphized.md.

Usage: python3 .claude/scripts/depolymorphize.py <deck-dir>
"""
import sys
import subprocess
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <deck-dir>", file=sys.stderr)
        sys.exit(2)

    deck_dir = sys.argv[1]
    script_dir = Path(__file__).parent
    project_root = Path.cwd()

    result = subprocess.run(
        [sys.executable, str(script_dir / "find-inheritables.py"), deck_dir],
        capture_output=True, text=True, check=True
    )
    files = [p for p in result.stdout.strip().splitlines() if p]

    if not files:
        print(f"No inheritable-*.md files found under {deck_dir}", file=sys.stderr)
        sys.exit(1)

    output_path = project_root / deck_dir / "depolymorphized.md"

    with open(output_path, "w") as out:
        for i, rel_path in enumerate(files):
            file_path = project_root / rel_path
            content = file_path.read_text()
            if i == 0:
                out.write(f"# {file_path.name}\n\n{content}")
            else:
                out.write(f"\n---\n\n# {file_path.name}\n\n{content}")

    print(f"✓ Depolymorphized {deck_dir} → {deck_dir}/depolymorphized.md")
    print(f"  Files: {', '.join(Path(f).name for f in files)}")


if __name__ == "__main__":
    main()
