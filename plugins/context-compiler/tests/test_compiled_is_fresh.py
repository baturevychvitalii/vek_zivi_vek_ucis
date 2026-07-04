"""
Tests for compiled-is-fresh.py exit codes:
  0 — up-to-date
  1 — stale (compiled missing or an input is newer)
  3 — broken #include (referenced file does not exist)
"""
import subprocess
import sys
import time
from pathlib import Path

PLUGIN_DIR = Path(__file__).parent.parent
SCRIPT = PLUGIN_DIR / "compiled-is-fresh.py"


def run(source: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(source)],
        capture_output=True,
        text=True,
        cwd=PLUGIN_DIR,
    )


class TestUpToDate:
    def test_exit_0_when_compiled_newer(self, tmp_path):
        source = tmp_path / "doc.md"
        source.write_text("# no includes\n")
        compiled = tmp_path / "doc.compiled.md"
        time.sleep(0.01)
        compiled.write_text("compiled\n")
        result = run(source)
        assert result.returncode == 0
        assert "up-to-date" in result.stdout


class TestStale:
    def test_exit_1_when_compiled_missing(self, tmp_path):
        source = tmp_path / "doc.md"
        source.write_text("# no includes\n")
        result = run(source)
        assert result.returncode == 1

    def test_exit_1_when_source_newer_than_compiled(self, tmp_path):
        source = tmp_path / "doc.md"
        compiled = tmp_path / "doc.compiled.md"
        compiled.write_text("compiled\n")
        time.sleep(0.01)
        source.write_text("# updated\n")
        result = run(source)
        assert result.returncode == 1
        assert "stale" in result.stdout

    def test_exit_1_when_included_file_newer(self, tmp_path):
        included = tmp_path / "base.md"
        included.write_text("# base\n")
        source = tmp_path / "doc.md"
        source.write_text(f"#include ./{included.name}\n")
        compiled = tmp_path / "doc.compiled.md"
        compiled.write_text("compiled\n")
        time.sleep(0.01)
        included.write_text("# base updated\n")
        result = run(source)
        assert result.returncode == 1
        assert "stale" in result.stdout


class TestBrokenInclude:
    def test_exit_3_when_include_missing(self, tmp_path):
        source = tmp_path / "doc.md"
        source.write_text("#include does-not-exist.md\n")
        compiled = tmp_path / "doc.compiled.md"
        time.sleep(0.01)
        compiled.write_text("compiled\n")
        result = run(source)
        assert result.returncode == 3
        assert "broken include" in result.stderr
