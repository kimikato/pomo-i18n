# tests/test_message_map_plural.py
# type: ignore

from pypomo.catalog import Catalog, CatalogMessage
from pypomo.mo.writer import _build_message_map


def test_message_map_plural():
    c = Catalog()
    c.languages = ["en"]
    c.nplurals = 2

    msg = CatalogMessage(
        "apple",
        singular="apple",
        plural="apples",
        translations={0: "apple", 1: "apples"},
    )
    c.add_message(msg)

    msgmap = _build_message_map(c)

    # plural key
    key = "apple\0apples"
    assert key in msgmap

    # plural forms are combined with \x00
    assert msgmap[key] == "apple\x00apples"
