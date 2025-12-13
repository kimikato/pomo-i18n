# src/pypomo/catalog_message.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass(slots=True)
class CatalogMessage:
    """
    Immutable-like message structure used by Catalog.

    - msgid: logical key
    - singular: primary translation or fallback (never empty)
    - plural: plural form msgid or None
    - translations:
        dict[int, str] such that:
            - 0 always exists (singular form)
            - if plural is present → 1..n_forms exist
    """

    msgid: str
    singular: str
    plural: str | None = None
    translations: Dict[int, str] = field(
        default_factory=lambda: dict[int, str]()
    )

    # ----------------------------------------
    # Normalization initializer
    # ----------------------------------------
    def __post_init__(self) -> None:
        # Guarantee singular consistency
        if not self.singular:
            self.singular = self.msgid

        # Normalize plural: "" -> None
        if self.plural == "":
            self.plural = None

        # Ensure translations[0] exists
        if 0 not in self.translations:
            self.translations[0] = self.singular

        # Remove empty translations and fall back correctly
        for idx, val in list(self.translations.items()):
            if not val:
                # idx = 0 -> fallback to singular
                if idx == 0:
                    self.translations[0] = self.singular
                else:
                    # idx > 0 -> fallback to plural or singular
                    fallback: str = self.plural or self.singular
                    self.translations[idx] = fallback

    # ----------------------------------------
    # Helper Constructors
    # ----------------------------------------
    @classmethod
    def from_singular(
        cls,
        msgid: str,
        msgstr: str = "",
    ) -> CatalogMessage:
        """
        Create a singular-only message.
        """
        singular: str = msgstr or msgid
        return cls(
            msgid=msgid,
            singular=singular,
            plural=None,
            translations={0: singular},
        )

    @classmethod
    def from_plural(
        cls,
        msgid: str,
        msgid_plural: str,
        forms: Dict[int, str],
    ) -> CatalogMessage:
        """
        Create a plural-aware message.

        forms: {0: "...", 1: "...", ...}
        Missing forms will be normalized in __post_init__.
        """
        singular: str = forms.get(0) or msgid
        return cls(
            msgid=msgid,
            singular=singular,
            plural=msgid_plural,
            translations=forms,
        )

    # ----------------------------------------
    # Accessor helpers for dict-like API
    # ----------------------------------------
    def as_plain(self) -> str:
        """Return the singular form."""
        return self.translations.get(0, self.singular)

    def get_plural(self, index: int) -> str:
        """Safe plural accessor."""
        return self.translations.get(index, self.plural or self.singular)
