# tests/test_mo_writer.py

import gettext
from pathlib import Path

from pypomo.catalog import Catalog
from pypomo.mo_writer import write_mo
from pypomo.parser.types import POEntry


def test_write_and_read_mo(tmp_path):
    # ----- Build catalog -----
    entries = [
        POEntry(
            msgid="",
            msgstr="Language: ja\nPlural-Forms: nplurals=1; plural=0;\n",
            msgid_plural=None,
            msgstr_plural={},
            comments=[],
        ),
        POEntry(
            msgid="Hello",
            msgstr="こんにちは",
            msgid_plural=None,
            msgstr_plural={},
            comments=[],
        ),
        POEntry(
            msgid="apple",
            msgstr="りんご",
            msgid_plural="apples",
            msgstr_plural={0: "りんご"},
            comments=[],
        ),
    ]

    cat = Catalog.from_po_entries(entries)

    mo_path = tmp_path / "messages.mo"
    write_mo(mo_path, cat)

    # ----- Read using Python's builtin gettext -----
    with mo_path.open("rb") as f:
        trans = gettext.GNUTranslations(f)

    assert trans.gettext("Hello") == "こんにちは"
    assert trans.ngettext("apple", "apples", 1) == "りんご"
    assert trans.ngettext("apple", "apples", 5) == "りんご"
