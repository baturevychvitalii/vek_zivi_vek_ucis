import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from include_graph import collect_inputs, resolve_include_path


class TestResolveIncludePath:
    def test_relative_path(self, tmp_path):
        from_file = tmp_path / "sub" / "file.md"
        result = resolve_include_path("./other.md", from_file, tmp_path)
        assert result == (tmp_path / "sub" / "other.md").resolve()

    def test_project_root_path(self, tmp_path):
        from_file = tmp_path / "sub" / "file.md"
        result = resolve_include_path("groves/lang.md", from_file, tmp_path)
        assert result == (tmp_path / "groves" / "lang.md").resolve()


class TestCollectInputs:
    def test_entry_only(self, tmp_path):
        entry = tmp_path / "a.md"
        entry.write_text("# no includes\n")
        result = collect_inputs(entry, tmp_path, set())
        assert result == [entry.resolve()]

    def test_single_include(self, tmp_path):
        b = tmp_path / "b.md"
        b.write_text("# b\n")
        a = tmp_path / "a.md"
        a.write_text(f"#include b.md\n")
        result = collect_inputs(a, tmp_path, set())
        assert result == [a.resolve(), b.resolve()]

    def test_transitive(self, tmp_path):
        c = tmp_path / "c.md"
        c.write_text("# c\n")
        b = tmp_path / "b.md"
        b.write_text("#include c.md\n")
        a = tmp_path / "a.md"
        a.write_text("#include b.md\n")
        result = collect_inputs(a, tmp_path, set())
        assert result == [a.resolve(), b.resolve(), c.resolve()]

    def test_deduplication(self, tmp_path):
        shared = tmp_path / "shared.md"
        shared.write_text("# shared\n")
        b = tmp_path / "b.md"
        b.write_text("#include shared.md\n")
        a = tmp_path / "a.md"
        a.write_text("#include b.md\n#include shared.md\n")
        result = collect_inputs(a, tmp_path, set())
        assert result.count(shared.resolve()) == 1

    def test_missing_include_raises(self, tmp_path):
        a = tmp_path / "a.md"
        a.write_text("#include missing.md\n")
        import pytest
        with pytest.raises(FileNotFoundError, match="missing.md"):
            collect_inputs(a, tmp_path, set())

    def test_missing_entry_raises(self, tmp_path):
        import pytest
        with pytest.raises(FileNotFoundError):
            collect_inputs(tmp_path / "nonexistent.md", tmp_path, set())
