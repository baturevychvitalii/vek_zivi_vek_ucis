"""
Tests for compiled-is-fresh.py: exit 0 with a FRESH/STALE stdout token for the two
normal outcomes; non-zero with a stderr token for a genuine error (missing source,
broken #include).
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
    def test_exit_0_with_fresh_token(self, tmp_path):
        source = tmp_path / "doc.md"
        source.write_text("# no includes\n")
        compiled = tmp_path / "doc.compiled.md"
        time.sleep(0.01)
        compiled.write_text("compiled\n")
        result = run(source)
        assert result.returncode == 0
        assert "FRESH" in result.stdout


class TestStale:
    def test_exit_0_with_stale_token_when_compiled_missing(self, tmp_path):
        source = tmp_path / "doc.md"
        source.write_text("# no includes\n")
        result = run(source)
        assert result.returncode == 0
        assert "STALE" in result.stdout

    def test_exit_0_with_stale_token_when_source_newer_than_compiled(self, tmp_path):
        source = tmp_path / "doc.md"
        compiled = tmp_path / "doc.compiled.md"
        compiled.write_text("compiled\n")
        time.sleep(0.01)
        source.write_text("# updated\n")
        result = run(source)
        assert result.returncode == 0
        assert "STALE" in result.stdout

    def test_exit_0_with_stale_token_when_included_file_newer(self, tmp_path):
        included = tmp_path / "base.md"
        included.write_text("# base\n")
        source = tmp_path / "doc.md"
        source.write_text(f"#include ./{included.name}\n")
        compiled = tmp_path / "doc.compiled.md"
        compiled.write_text("compiled\n")
        time.sleep(0.01)
        included.write_text("# base updated\n")
        result = run(source)
        assert result.returncode == 0
        assert "STALE" in result.stdout


class TestBrokenInclude:
    def test_nonzero_exit_when_include_missing(self, tmp_path):
        source = tmp_path / "doc.md"
        source.write_text("#include does-not-exist.md\n")
        compiled = tmp_path / "doc.compiled.md"
        time.sleep(0.01)
        compiled.write_text("compiled\n")
        result = run(source)
        assert result.returncode != 0
        assert "BROKEN_INCLUDE" in result.stderr


class TestSourceNotFound:
    def test_nonzero_exit_when_source_missing(self, tmp_path):
        source = tmp_path / "does-not-exist.md"
        result = run(source)
        assert result.returncode != 0
        assert "SOURCE_NOT_FOUND" in result.stderr
