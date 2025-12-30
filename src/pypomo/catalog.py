# src/pypomo/catalog.py

from __future__ import annotations

from collections.abc import ItemsView, Iterable, KeysView, Mapping, ValuesView
from typing import Dict, Iterator, List, TypeVar, cast, overload

from pypomo.catalog_message import CatalogMessage
from pypomo.parser.types import POEntry
from pypomo.utils.plural_forms import PluralRule

_T = TypeVar("_T")
_MISSING = object()


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

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"messages={len(self._get_messages())},"
            f"language={self.effective_language!r},"
            f"nplurals={self.effective_nplurals},"
            f"header={bool(self._get_header())}"
            f")"
        )

    # ----------------------------------------
    # Internal API for __messages
    # ----------------------------------------
    def _get_messages(self) -> Dict[str, CatalogMessage]:
        return self.__messages

    def _set_messages(self, messages: Dict[str, CatalogMessage]) -> None:
        self.__messages = messages

    def _get_message(self, msgid: str) -> CatalogMessage | None:
        return self.__messages.get(msgid)

    def _set_message(self, message: CatalogMessage) -> None:
        if message.msgid == "":
            # Header is always an explicit override
            self._set_header(message.singular, overwrite_plural=True)
        self.__messages[message.msgid] = message

    # ----------------------------------------
    # Internal API for header
    # ----------------------------------------
    def _get_header(self) -> str | None:
        return self._header_raw

    def _set_header(
        self, value: str, *, overwrite_plural: bool = False
    ) -> None:
        """
        Set raw header msgstr and optionally (re)load plural rules.

        overwrite_plural:
            - False (default):
                Do not override existing plural_rule / nplurals.
            - True:
                Always re-parse Plural-Forms from header.
        """
        self._header_raw = value

        if overwrite_plural or self.plural_rule is None:
            self._load_header(value)

    # ----------------------------------------
    # Private getters for internal state
    # ----------------------------------------
    def _iter_messages(self) -> ValuesView[CatalogMessage]:
        """
        Internal-only: iterate over stored Message objects.
        """
        messages: Dict[str, CatalogMessage] = self._get_messages()
        return messages.values()

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
        message: CatalogMessage | None = self._get_message(msgid)
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
        message: CatalogMessage | None = self._get_message(singular)

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
        self._set_message(message)

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
                catalog._set_header(entry.msgstr, overwrite_plural=True)
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
        return self._get_header() or ""

    # ----------------------------------------
    # Convenience adders
    # ----------------------------------------
    def add_singular(self, msgid: str, msgstr: str) -> None:
        # Fallback: empty msgstr → use msgid
        singular = msgstr if msgstr else msgid

        self._set_message(
            CatalogMessage(
                msgid=msgid,
                singular=singular,
                plural=None,
                translations={},
            )
        )

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

        self._set_message(
            CatalogMessage(
                msgid=msgid,
                singular=singular,
                plural=msgid_plural,
                translations=plural_map,
            )
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

        Does NOT invent a default ("C" or "en") — gettext compatible
        """
        return self.languages[0] if self.languages else None

    # ----------------------------------------
    # Dict-like API (v0.2.0: singular only)
    # ----------------------------------------
    def __getitem__(self, key: str) -> str:
        """
        Dict-like lookup (gettext-compatible).

        Behavior:
            - If key == "":
                return header msgstr
            - If translation exists:
                return translated singular form
            - Otherwise:
                return key itself

        Notes:
            - Never raises KeyError (gettext compatible)
            - Plural forms are NOT handled here (v0.2.0)
        """
        if not isinstance(key, str):
            raise TypeError("Catalog keys must be str")

        # Header access
        if key == "":
            return self.header_msgstr()

        message = self._get_message(key)
        if message is None:
            return key

        # No plural translations → singular
        if not message.translations:
            return message.singular

        return message.translations.get(0, message.singular)

    def __setitem__(self, key: str, value: str) -> None:
        """
        Dict-like assignment (singular only).

        Examples:
            catalog["hello"] = "こんにちは"
            catalog[""] = "Project-Id-Version: Demo\\nLanguage: ja\\n"

        Notes:
            - Plural forms are NOT supported here (v0.2.0).
            - Header (msgid == "") is allowed and overwrites existing header.
        """
        if not isinstance(key, str):
            raise TypeError("Catalog keys must be str")

        if not isinstance(value, str):
            raise TypeError("Catalog values must be str")

        message = CatalogMessage.from_singular(msgid=key, msgstr=value)
        self._set_message(message)

    def __contains__(self, key: object) -> bool:
        """
        Dict-like membership test (gettext-compatible).

        Behavior:
            - key == "" -> True (header exists)
            - key is not str -> False
            - msgid exists in catalog -> True
            - otherwise -> False
        """
        if not isinstance(key, str):
            return False

        # Header always considered present
        if key == "":
            return bool(self._get_header())

        return bool(self._get_message(key) is not None)

    def __iter__(self) -> Iterator[str]:
        """
        Return an iterator over message ids (keys).

        Synonym for keys().
        """
        return iter(self._get_messages())

    def keys(self) -> KeysView[str]:
        """
        Return a view over message ids (including header with key "")
        """
        return self._get_messages().keys()

    def values(self) -> ValuesView[CatalogMessage]:
        """
        Return a view over CatalogMessage objects (including header)
        """
        return self._get_messages().values()

    def items(self) -> ItemsView[str, CatalogMessage]:
        """
        Return a view over (msgid, CatalogMessage) pairs (including header)
        """
        return self._get_messages().items()

    def __len__(self) -> int:
        """
        Return the number of messages (including header)
        """
        return len(self._get_messages())

    # fmt: off
    @overload
    def get(self, key: str) -> CatalogMessage | str:
        ...

    @overload
    def get(self, key: str, default: _T) -> CatalogMessage | _T:
        ...
    # fmt: on

    def get(
        self,
        key: str,
        default: object = _MISSING,
    ) -> CatalogMessage | _T | str:
        """
        Return message for key if present, else fallback.

        Behavior:
            - If key exists:
                return CatalogMessage
            - If key does not exist and default is provided:
                return default
            - If key does not exist and default is NOT provided:
                returns key itself (gettext-compatible fallback)

        Note:
            Catalog.get() differs from dict.get() behavior.
            When default is not provided, missing keys fallback to msgid
            for gettext compatibility.
        """
        if not isinstance(key, str):
            raise TypeError("Catalog keys must be str")

        message = self._get_message(key)
        if message is not None:
            return message

        if default is _MISSING:
            return key

        return cast(_T, default)

    def copy(self) -> Catalog:
        """
        Return a shallow copy of this Catalog.

        Notes:
        - CatalogMessage objects are shared.
        - Internal dict/list containers are copied.
        """
        new = Catalog(
            domain=self.domain,
            localedir=self.localedir,
            languages=list(self.languages),
        )

        # messages (shadow copy)
        new._set_messages(self._get_messages().copy())

        # header + plural info
        new._header_raw = self._header_raw
        new.plural_rule = self.plural_rule
        new.nplurals = self.nplurals

        return new

    def update(
        self,
        other: Catalog | Mapping[str, CatalogMessage],
    ) -> None:
        """
        Update catalog messages from another mapping or iterable.

        Dict-like API (gettext-compatible):

            catalog.update(other)

        Behavior:
            - Keys must be str
            - Values must be CatalogMessage
            - Existing keys are overwritten
            - Header (msgid == "") is allowed and updates header state

        Note:
            Mapping[str, CatalogMessage] is assumed when isinstance(other, Mapping).
        """
        # Case 1: Catalog
        if isinstance(other, Catalog):
            for _, message in other.items():
                self._set_message(message)
            return

        # Case 2: Mapping[str, CatalogMessage]
        if isinstance(other, Mapping):
            for key, message in other.items():
                if not isinstance(key, str):
                    raise TypeError("Catalog keys must be str")
                if not isinstance(message, CatalogMessage):
                    raise TypeError("Catalog values must be CatalogMessage")
                # Delegate to internal setter (handles headar correctly)
                self._set_message(message)
            return

        raise TypeError(
            "Catalog.update() expects Catalog or Mapping[str, CatalogMessage]"
        )

    def __delitem__(self, key: str) -> None:
        raise TypeError("Catalog does not support item deletion")
