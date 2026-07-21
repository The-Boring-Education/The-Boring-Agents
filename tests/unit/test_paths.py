"""Unit tests for safe path helpers."""

import os
from pathlib import Path

import pytest

from src.utils.paths import resolve_under_roots, safe_filename, safe_join_under


class TestSafeFilename:
    def test_accepts_simple_name(self):
        assert safe_filename("data.json") == "data.json"

    def test_rejects_empty(self):
        with pytest.raises(ValueError):
            safe_filename("")

    def test_rejects_dot_dot(self):
        with pytest.raises(ValueError):
            safe_filename("..")


class TestSafeJoinUnder:
    def test_joins_under_base(self, temp_dir):
        result = safe_join_under(temp_dir, "a.json")
        assert str(result).startswith(str(Path(temp_dir).resolve()))


class TestResolveUnderRoots:
    def test_absolute_inside_root(self, temp_dir):
        root = Path(temp_dir) / "out"
        root.mkdir()
        file_path = root / "x.json"
        file_path.write_text("{}", encoding="utf-8")

        assert resolve_under_roots(str(file_path), [str(root)]) == file_path.resolve()

    def test_absolute_outside_root(self, temp_dir):
        root = Path(temp_dir) / "out"
        root.mkdir()
        outside = Path(temp_dir) / "outside.json"
        outside.write_text("{}", encoding="utf-8")

        with pytest.raises(ValueError):
            resolve_under_roots(str(outside), [str(root)])
