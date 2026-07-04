import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from preprocess import preprocess


class TestPreprocess:
    def test_no_includes(self, tmp_path):
        entry = tmp_path / "a.md"
        entry.write_text("# hello\n")
        result = preprocess(entry, tmp_path, set(), set())
        assert result == "# hello\n"

    def test_single_include_merged(self, tmp_path):
        b = tmp_path / "b.md"
        b.write_text("# b content\n")
        a = tmp_path / "a.md"
        a.write_text("#include b.md\n# a content\n")
        result = preprocess(a, tmp_path, set(), set())
        assert "# b content" in result
        assert "# a content" in result
        assert "#include" not in result

    def test_deduplication(self, tmp_path):
        shared = tmp_path / "shared.md"
        shared.write_text("# shared\n")
        b = tmp_path / "b.md"
        b.write_text("#include shared.md\n")
        a = tmp_path / "a.md"
        a.write_text("#include b.md\n#include shared.md\n")
        result = preprocess(a, tmp_path, set(), set())
        assert result.count("# shared") == 1

    def test_missing_include_raises(self, tmp_path):
        a = tmp_path / "a.md"
        a.write_text("#include missing.md\n")
        with pytest.raises(FileNotFoundError, match="missing.md"):
            preprocess(a, tmp_path, set(), set())

    def test_circular_include_raises(self, tmp_path):
        a = tmp_path / "a.md"
        b = tmp_path / "b.md"
        a.write_text("#include b.md\n")
        b.write_text("#include a.md\n")
        with pytest.raises(ValueError, match="[Cc]ircular"):
            preprocess(a, tmp_path, set(), set())
