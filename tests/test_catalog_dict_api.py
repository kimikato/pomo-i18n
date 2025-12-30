# tests/test_catalog_dict_api.py
# type: ignore

# tests/test_catalog_dict_api.py

import pytest

from pypomo.catalog import Catalog
from pypomo.catalog_message import CatalogMessage

# ----------------------------------------
# __getitem__
# ----------------------------------------


def test_getitem_missing_returns_key():
    catalog = Catalog()

    assert catalog["hello"] == "hello"


def test_getitem_existing_returns_translation():
    catalog = Catalog()
    catalog["hello"] = "こんにちは"

    assert catalog["hello"] == "こんにちは"


def test_getitem_header():
    catalog = Catalog()
    catalog[""] = "Language: ja\n"

    assert "Language: ja" in catalog[""]


def test_getitem_non_str_key_raises_typeerror():
    catalog = Catalog()

    with pytest.raises(TypeError):
        _ = catalog[123]  # type: ignore[arg-type]


# ----------------------------------------
# __setitem__
# ----------------------------------------


def test_setitem_singular_creates_message():
    catalog = Catalog()
    catalog["hello"] = "こんにちは"

    msg = catalog.get("hello")
    assert isinstance(msg, CatalogMessage)
    assert msg.singular == "こんにちは"


def test_setitem_empty_string_sets_header():
    catalog = Catalog()
    catalog[""] = "Project-Id-Version: Demo\n"

    assert "Project-Id-Version" in catalog.header_msgstr()


def test_setitem_non_str_value_raises_typeerror():
    catalog = Catalog()

    with pytest.raises(TypeError):
        catalog["hello"] = 123  # type: ignore[assignment]


# ----------------------------------------
# __contains__
# ----------------------------------------


def test_contains_existing_key():
    catalog = Catalog()
    catalog["hello"] = "こんにちは"

    assert "hello" in catalog


def test_contains_missing_key():
    catalog = Catalog()

    assert "missing" not in catalog


def test_contains_header_key():
    catalog = Catalog()
    catalog[""] = "Language: ja\n"

    assert "" in catalog


def test_contains_non_str_key():
    catalog = Catalog()

    assert 123 not in catalog  # type: ignore[operator]


# ----------------------------------------
# get()
# ----------------------------------------


def test_get_without_default_returns_key():
    catalog = Catalog()

    # gettext-compatible fallback
    assert catalog.get("hello") == "hello"


def test_get_with_default_returns_default():
    catalog = Catalog()

    assert catalog.get("hello", "fallback") == "fallback"


def test_get_existing_returns_message():
    catalog = Catalog()
    catalog["hello"] = "こんにちは"

    msg = catalog.get("hello")
    assert isinstance(msg, CatalogMessage)
    assert msg.singular == "こんにちは"


def test_get_non_str_key_raise_typeerror():
    catalog = Catalog()

    # non-str key without default -> TypeError
    with pytest.raises(TypeError):
        catalog.get(123)

    # non-str key with default -> TypeError
    with pytest.raises(TypeError):
        catalog.get(123, "x")


# ----------------------------------------
# iteration / views
# ----------------------------------------


def test_iter_returns_keys():
    catalog = Catalog()
    catalog["hello"] = "こんにちは"
    catalog[""] = "Language: ja\n"

    keys = list(catalog)
    assert "hello" in keys
    assert "" in keys


def test_keys_values_items():
    catalog = Catalog()
    catalog["hello"] = "こんにちは"

    keys = list(catalog.keys())
    values = list(catalog.values())
    items = list(catalog.items())

    assert keys == ["hello"]
    assert isinstance(values[0], CatalogMessage)
    assert items[0][0] == "hello"


def test_len():
    catalog = Catalog()
    catalog["hello"] = "こんにちは"

    assert len(catalog) == 1


# ----------------------------------------
# copy()
# ----------------------------------------


def test_copy_creates_independent_catalog():
    catalog = Catalog()
    catalog["hello"] = "こんにちは"
    catalog[""] = "Language: ja\n"

    new = catalog.copy()

    assert new is not catalog
    assert new["hello"] == "こんにちは"
    assert new.header_msgstr() == catalog.header_msgstr()


# ----------------------------------------
# update()
# ----------------------------------------


def test_update_with_mapping():
    catalog = Catalog()

    msg = CatalogMessage.from_singular("hello", "こんにちは")
    catalog.update({"hello": msg})

    assert catalog["hello"] == "こんにちは"


def test_update_with_other_catalog():
    c1 = Catalog()
    c1["hello"] = "こんにちは"

    c2 = Catalog()
    c2.update(c1)

    assert c2["hello"] == "こんにちは"


# ----------------------------------------
# __delitem__
# ----------------------------------------


def test_delitem_is_not_supported():
    catalog = Catalog()
    catalog["hello"] = "こんにちは"

    with pytest.raises(TypeError):
        del catalog["hello"]
