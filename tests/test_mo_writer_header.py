# tests/test_mo_writer_header.py
# type: ignore

from pathlib import Path

import polib

from pypomo.catalog import Catalog, CatalogMessage
from pypomo.mo.writer import write_mo


def test_write_mo_with_fallback_header(tmp_path: Path):
    """write_mo() が fallback header を正しく生成し、
    生成された .mo ファイルを polib が正しく読み取れることを確認する。
    """
    # --- Catalog 準備 ---
    c = Catalog()
    c.languages = ["en"]
    c.nplurals = 2

    # 通常のメッセージ
    c.add_message(
        CatalogMessage("hello", singular="hello", translations={0: "Hello"})
    )

    # --- write_mo() 実行 ---
    mo_path = tmp_path / "out.mo"
    write_mo(mo_path, c)

    # --- polib で読み戻す ---
    mo = polib.mofile(str(mo_path))

    # --- header 検証 ---
    assert mo.metadata["Project-Id-Version"] == "PACKAGE VERSION"
    assert mo.metadata["MIME-Version"] == "1.0"
    assert mo.metadata["Content-Type"] == "text/plain; charset=UTF-8"
    assert mo.metadata["Language"] == "en"
    assert mo.metadata["Plural-Forms"] == "nplurals=2; plural=(n != 1);"

    # --- 通常メッセージの検証 ---
    assert mo.find("hello").msgstr == "Hello"
