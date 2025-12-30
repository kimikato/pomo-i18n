# tests/test_catalog_dict_like.py
# type: ignore

import pytest

from pypomo.catalog import Catalog

# ----------------------------------------
# 1. Basic: singular translation
# ----------------------------------------


def test_dict_like_set_and_get():
    cat = Catalog()

    cat["hello"] = "こんにちは"

    assert cat["hello"] == "こんにちは"
    assert cat.gettext("hello") == "こんにちは"


def test_dict_like_missing_key_returns_msgid():
    cat = Catalog()

    # Missing key should return msgid itself (gettext-compatible)
    assert cat["missing"] == "missing"
    assert cat.get("missing") == "missing"


def test_dict_like_get_with_default():
    cat = Catalog()

    # dict-like get(key, default) behavior
    assert cat.get("missing", "DEFAULT") == "DEFAULT"


# ----------------------------------------
# 2. Header handling (msgid == "")
# ----------------------------------------


def test_dict_like_set_header():
    cat = Catalog()

    header = "Language: ja\nPlural-Forms: nplurals=1; plural=0;\n"
    cat[""] = header

    # Header is stored and retrievable
    assert cat[""] == header
    assert cat.header_msgstr() == header

    # Plural-Forms should be parsed from header
    assert cat.nplurals == 1


def test_dict_like_header_in_operator():
    cat = Catalog()

    # Header does not exist initially
    assert "" not in cat

    cat[""] = "Language: en\n"

    # Header key should now be present
    assert "" in cat


# ----------------------------------------
# 3. Override behavior
# ----------------------------------------


def test_dict_like_override_value():
    cat = Catalog()

    cat["hello"] = "こんにちは"
    cat["hello"] = "やあ"

    # Latest assignment wins
    assert cat["hello"] == "やあ"


# ----------------------------------------
# 4. `in` operator support
# ----------------------------------------


def test_dict_like_in_operator():
    cat = Catalog()

    cat["hello"] = "こんにちは"

    assert "hello" in cat
    assert "missing" not in cat


# ----------------------------------------
# 5. Unsupported operations (v0.2.0 scope)
# ----------------------------------------


def test_dict_like_plural_assignment_is_not_supported():
    cat = Catalog()

    # Plural assignment is intentionally not supported in v0.2.0
    with pytest.raises(TypeError):
        cat["apple"] = {0: "りんご", 1: "りんごたち"}


def test_dict_like_delete_is_not_supported():
    cat = Catalog()

    cat["hello"] = "こんにちは"

    # Deletion is not supported (Catalog is append/override-only)
    with pytest.raises(TypeError):
        del cat["hello"]
