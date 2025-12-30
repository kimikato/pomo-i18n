# tests/test__build_header.py
# type: ignore

import pytest

from pypomo.catalog import Catalog
from pypomo.mo.writer import _build_header


class DummyCatalog:
    """
    A tiny stub for Catalog only for header testing.
    """

    def __init__(self, header: str = "", languages=None, nplurals=None):
        self._header = header
        self.languages = languages or []
        self.nplurals = nplurals

    def header_msgstr(self) -> str:
        return self._header

    @property
    def effective_language(self) -> str | None:
        return self.languages[0] if self.languages else None

    @property
    def effective_nplurals(self) -> int:
        return self.nplurals if self.nplurals is not None else 2


def test_build_header_with_explicit_header():
    """
    Case 1: Header exists in the PO → return as-is (normalized).
    """
    cat = DummyCatalog(header="Project-Id-Version: Demo\nLanguage: en\n")

    result = _build_header(cat)

    # 行末に必ず改行がつく
    assert result.endswith("\n")

    # 余計な CR は削除されているか？
    assert "Project-Id-Version: Demo" in result
    assert "Language: en" in result

    # raw をそのまま返すので、Plural-Forms は追加されない
    assert "Plural-Forms" not in result


def test_build_header_minimal_default():
    """
    Case 2: No header → auto-generate a minimal gettext header.
    """
    cat = DummyCatalog(header="")

    result = _build_header(cat)

    # 必須項目が含まれている
    assert "Project-Id-Version: PACKAGE VERSION" in result
    assert "MIME-Version: 1.0" in result
    assert "Content-Type: text/plain; charset=UTF-8" in result
    assert result.endswith("\n")

    # Plural-Forms (default nplurals=2)
    assert "Plural-Forms: nplurals=2; plural=(n != 1);" in result


def test_build_header_with_language_and_nplurals():
    """
    Case 3: languages + plural rules.
    """
    cat = DummyCatalog(header="", languages=["fr"], nplurals=3)

    result = _build_header(cat)

    assert "Language: fr" in result
    assert "Plural-Forms: nplurals=3;" in result
