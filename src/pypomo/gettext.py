# src/pypomo/gettext.py

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .catalog import Catalog
from .parser.po_parser import POParser

# Global catalog for convinience
_default_catalog = Catalog()


def gettext(msgid: str) -> str:
    """Translate msgid using the default catalog."""
    result = _default_catalog.gettext(msgid)
    # Catalog.gettext() returns str, but mypy needs the cast via annotation
    return result


def ngettext(singular: str, plural: str, n: int) -> str:
    """Plural-aware translate using the default catalog."""
    result = _default_catalog.ngettext(singular, plural, n)
    return result


def translation(
    domain: str, localedir: str, languages: list[str] | None = None
) -> Catalog:
    """
    Load translations from .po files for the selected domain/languages.

    This is a strict/mypy-friendly implementation.
    """
    catalog = Catalog(
        domain=domain,
        localedir=localedir,
        languages=list(languages) if languages is not None else None,
    )

    langs = list(languages) if languages is not None else []
    parser = POParser()

    for lang in langs:
        po_path = Path(localedir) / lang / "LC_MESSAGES" / f"{domain}.po"
        print(f"path: {po_path}")
        if po_path.exists():
            entries = parser.parse(po_path)
            part = Catalog.from_po_entries(entries)
            # bulk update is fully typed
            catalog.bulk_update(part._messages)

    return catalog
