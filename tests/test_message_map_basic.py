# tests/test_message_map_basic.py
# type: ignore

from pypomo.catalog import Catalog, CatalogMessage
from pypomo.mo.writer import _build_message_map


def test_message_map_basic():
    c = Catalog()
    c.languages = ["ja"]
    c.nplurals = 2

    c.add_message(
        CatalogMessage(
            "hello", singular="hello", translations={0: "こんにちは"}
        )
    )

    msgmap = _build_message_map(c)

    assert "" in msgmap  # header
    assert "hello" in msgmap
    assert msgmap["hello"] == "こんにちは"
