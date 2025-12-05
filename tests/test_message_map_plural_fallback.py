# tests/test_message_map_plural_fallback.py
# type: ignore

from pypomo.catalog import Catalog, CatalogMessage
from pypomo.mo.writer import _build_message_map


def test_message_map_plural_fallback():
    """plural forms が不足している場合、fallback が使われるか"""
    c = Catalog()
    c.languages = ["en"]
    c.nplurals = 3  # 3 つ必要なケース

    msg = CatalogMessage(
        "cat",
        singular="cat",
        plural="cats",
        translations={0: "cat", 1: "cats"},  # form 2 が欠けている
    )
    c.add_message(msg)

    msgmap = _build_message_map(c)

    key = "cat\0cats"

    # form2 は fallback → plural を使用（仕様通り）
    assert msgmap[key] == "cat\x00cats\x00cats"
