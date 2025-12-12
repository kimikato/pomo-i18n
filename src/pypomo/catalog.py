# src/pypomo/catalog.py

from __future__ import annotations

from collections.abc import Iterable, ValuesView
from dataclasses import dataclass, field
from typing import Dict, List

from pypomo.parser.types import POEntry
from pypomo.utils.plural_forms import PluralRule


@dataclass(slots=True)
class CatalogMessage:
    """
    Represents a single resolved message in a catalog.
    """

    msgid: str
    singular: str
    plural: str | None = None
    translations: Dict[int, str] = field(
        default_factory=lambda: dict[int, str]()
    )


class Catalog:
    """
    In-memory message catalog.

    Responsibilities:
        - Provide gettext / ngettext translation lookups
        - Manage plural rules via Plural-Forms
        - Build message objects from POEntry structures

    Internal notice:
        - __messages is considered private
        - External code should not rely on its structure
    """

    def __init__(
        self,
        domain: str | None = None,
        localedir: str | None = None,
        languages: Iterable[str] | None = None,
    ) -> None:
        self.domain = domain
        self.localedir = localedir

        # Accept any iterable, but normalize to list[str]
        self.languages: list[str] = (
            list(languages) if languages is not None else []
        )

        # Private internal storage of messages
        self.__messages: Dict[str, CatalogMessage] = {}

        # Plural forms evaluator (None until loaded from header)
        self.plural_rule: PluralRule | None = None
        # Keep nplurals for compatibility with tests / mo_writer
        self.nplurals: int | None = None

        # Raw header message (msgid == "")
        self._header_raw: str = ""

    # ----------------------------------------
    # Private getters for internal state
    # ----------------------------------------
    def _iter_messages(self) -> ValuesView[CatalogMessage]:
        """
        Internal-only: iterate over stored Message objects.
        """
        return self.__messages.values()

    # ----------------------------------------
    # Header: Parse plural-forms
    # ----------------------------------------
    def _load_header(self, header_msgstr: str) -> None:
        """
        Try to extract a Plural-Forms rule from the header msgstr.

        The header is a concatenated string of lines like:
            "Language: en\\n"
            "Plural-Forms: nplurals=2; plural=(n != 1);\\n"
        """
        if "Plural-Forms" not in header_msgstr:
            return

        try:
            rule = PluralRule.from_header(header_msgstr)
            self.plural_rule = rule
            self.nplurals = rule.nplurals
        except Exception:
            # Fail-safe: leave plural_rule / nplurals as-is
            pass

    # ----------------------------------------
    # Plural index helper (gettext-compatible)
    # ----------------------------------------
    def _select_plural_index(self, n: int) -> int:
        """
        Compute plural index for n, using gettext-compatible fallback.

        Rules:
            - If plural_rule is present -> use it.
            - Otherwise -> default rule: index = 0 if n == 1 else 1
              (this matches gettext's built-in default when Plural-Forms
               is not specified: nplurals=2; plural=(n != 1))
        """
        if self.plural_rule is None:
            return 0 if n == 1 else 1
        return self.plural_rule(n)

    # ----------------------------------------
    # Lookup API
    # ----------------------------------------
    def gettext(self, msgid: str) -> str:
        """Return translated string or msgid if not found."""
        message = self.__messages.get(msgid)
        if message is None:
            return msgid

        # No plural translations -> use singular
        if not message.translations:
            return message.singular

        # Singular form = index 0
        return message.translations.get(0, message.singular)

    def ngettext(self, singular: str, plural: str, n: int) -> str:
        """
        Return plural-aware translation.

        Behavior is aligned with gettext:

            - If no translation exists:
                singular if n == 1 else plural

            - Otherwise:
                1) compute plural index i
                2) if msgstr[i] exists -> return it
                3) else if msgstr[0] exists -> return msgstr[0]
                4) else if singular exists -> return singular
                5) else -> fall back to original plural
        """
        message = self.__messages.get(singular)

        # 1) No translation at all -> behave like gettext
        if message is None:
            # No translation → return original strings
            return singular if n == 1 else plural

        # 2) Compute plural index using gettext-like rule
        index = self._select_plural_index(n)
        forms = message.translations

        # 3) Use exact plural form if available
        if index in forms:
            return forms[index]

        # 4) Fallback: msgstr[0] if present
        if 0 in forms:
            return forms[0]

        # 5) Fallback: singular (translated)
        if message.singular:
            return message.singular

        # 6) Very last resort: original plural argument
        return plural

    # ----------------------------------------
    # Mutation helpers
    # ----------------------------------------
    def add_message(self, message: CatalogMessage) -> None:
        """Add or replace a single message."""
        self.__messages[message.msgid] = message

    def merge(self, other: Catalog) -> None:
        """
        Merge messages from another Catalog.

        This is a public helper that keeps __messages private, while still
        allowing catalogs built from different PO files to be merged.
        """
        # Accessing __messages is allowed from within the same class
        self.__messages.update(other.__messages)

        # If the current catalog has no plural_rule yet, inherit from other
        if self.plural_rule is None and other.plural_rule is not None:
            self.plural_rule = other.plural_rule
            self.nplurals = other.nplurals

    # ----------------------------------------
    # Construction helpers
    # ----------------------------------------
    @classmethod
    def from_po_entries(cls, entries: List[POEntry]) -> Catalog:
        """
        Build a Catalog from a list of POEntry objects.

        This will:
            - Extract Plural-Forms from the header entry (msgid == "")
            - Convert all non-header entries into Message instances
        """
        catalog = cls()

        # messages
        for entry in entries:

            # header
            if entry.msgid == "":
                catalog._header_raw = entry.msgstr
                catalog._load_header(entry.msgstr)
                continue

            # normal entry
            # singular msgstr or fallback to msgid
            singular = entry.msgstr if entry.msgstr else entry.msgid

            msg = CatalogMessage(
                msgid=entry.msgid,
                singular=singular,
                plural=entry.msgid_plural,
                translations=entry.msgstr_plural.copy(),
            )

            catalog.add_message(msg)

        return catalog

    # ----------------------------------------
    # Header helpers
    # ----------------------------------------
    def header_msgstr(self) -> str:
        """Return raw header msgstr (msgid == "")."""
        return self._header_raw or ""

    # ----------------------------------------
    # Convenience adders
    # ----------------------------------------
    def add_singular(self, msgid: str, msgstr: str) -> None:
        # Fallback: empty msgstr → use msgid
        singular = msgstr if msgstr else msgid

        self.__messages[msgid] = CatalogMessage(
            msgid=msgid,
            singular=singular,
            plural=None,
            translations={},
        )

        # If Header (msgid == ""), also update _header_raw
        if msgid == "":
            self._header_raw = singular
            # If no plural_rule yet, interpret it here
            if self.plural_rule is None:
                self._load_header(singular)

    def add_plural(
        self,
        msgid: str,
        msgid_plural: str,
        forms: list[str],
    ) -> None:
        # If form[0] exists, it will be used as singular,
        # otherwise msgid will be used as fallback.
        singular: str = ""
        if forms:
            singular = forms[0]
        else:
            singular = msgid

        plural_map: Dict[int, str] = {i: f for i, f in enumerate(forms)}

        self.__messages[msgid] = CatalogMessage(
            msgid=msgid,
            singular=singular,
            plural=msgid_plural,
            translations=plural_map,
        )

    # ----------------------------------------
    # Effective properties (safe defaults)
    # ----------------------------------------
    @property
    def effective_nplurals(self) -> int:
        """
        Always return a valid nplurals value.
        Default is 2 (gettext fallback), which matches common behavior
        when Plural-Forms is missing.
        """
        if self.nplurals is not None:
            return self.nplurals
        return 2

    @property
    def effective_language(self) -> str | None:
        """
        Returns main language or None.

        Does NOT invent a default ("C" や "en") — gettext compatible
        """
        return self.languages[0] if self.languages else None
