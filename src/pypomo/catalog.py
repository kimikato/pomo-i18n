# src/pypomo/catalog.py

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Mapping, Tuple

from pypomo.parser.types import POEntry

# Type for plural evaluation function
PluralEval = Callable[[int], int]


@dataclass(slots=True)
class Message:
    """Represents a single resolved message in a catalog."""

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
    - Hold runtime Message objects
    - Be format-agnostic (.po/.mo loading happens externally)
    """

    def __init__(
        self,
        domain: str | None = None,
        localedir: str | None = None,
        languages: Iterable[str] | None = None,
    ) -> None:
        self.domain = domain
        self.localedir = localedir
        self.languages = list(languages) if languages is not None else None

        self._messages: Dict[str, Message] = {}

        # plural forms evaluator
        self.plural_eval: PluralEval | None = None
        self.nplurals: int = 2  # default: English-like

    # ----------------------------------------
    # Header: Parse plural-forms
    # ----------------------------------------
    def _set_plural_forms(self, nplurals: int, expression: str) -> None:
        """Register plural rule from gettext header."""
        self.nplurals = nplurals

        # gettext -> Python expression
        expr = expression

        # Replace logical AND/OR
        expr = expr.replace("&&", " and ")
        expr = expr.replace("||", " or ")

        # Replace standalone '!' (but not '!=')
        expr = re.sub(r"!(?!=)", " not ", expr)

        # minimal ternary operator conversion: cond ? a : b
        if "?" in expr and ":" in expr:
            expr = self._convert_ternary(expr)

        # compile into safe eval object
        code = compile(expr, "<plural-form>", "eval")

        def plural_func(n: int) -> int:
            return int(eval(code, {"__builtins__": {}}, {"n": n}))

        self.plural_eval = plural_func

    def _convert_ternary(self, s: str) -> str:
        """
        Convert C-style ternary operator to Python's `a if cond else b`.

        This is simplified but covers all known gettext plural rules.
        pattern:  cond ? val1 : val2
        """
        q = s.find("?")
        colon = s.find(":", q)

        if q == -1 or colon == -1:
            return s

        cond = s[:q].strip()
        val1 = s[q + 1 : colon].strip()
        val2 = s[colon + 1 :].strip()

        return f"({val1} if {cond} else {val2})"

    # ----------------------------------------
    # Lookup API
    # ----------------------------------------
    def gettext(self, msgid: str) -> str:
        message = self._messages.get(msgid)
        if message is None:
            return msgid

        # No plural translations -> use singular
        if not message.translations:
            return message.singular

        # Default singular form
        return message.translations.get(0, message.singular)

    def ngettext(self, singular: str, plural: str, n: int) -> str:
        message = self._messages.get(singular)

        if message is None:
            return singular if n == 1 else plural

        # plural index
        if self.nplurals == 1:
            index = 0
        else:
            # usually, plural evaluator
            if self.plural_eval is None:
                index = 0 if n == 1 else 1
            else:
                index = self.plural_eval(n)
                if index < 0 or index >= self.nplurals:
                    index = 0

        # gettext-compatible plural lookup
        # 1. Returns the translation if it exists
        if index in message.translations:
            return message.translations[index]

        # 2. fallback (if translation not exists)
        #   index = 0 -> singular
        #   index > 0 -> plural (msgid_plural or English plural)
        return message.singular if index == 0 else (message.plural or plural)

    # ----------------------------------------
    # Mutation helpers
    # ----------------------------------------
    def add_message(self, message: Message) -> None:
        self._messages[message.msgid] = message

    def bulk_update(self, messages: Mapping[str, Message]) -> None:
        self._messages.update(messages)

    # ----------------------------------------
    # Construction helpers
    # ----------------------------------------
    @classmethod
    def from_po_entries(cls, entries: List[POEntry]) -> Catalog:
        """Create a Catalog from a list of parsed POEntry objects."""
        catalog = cls()

        # Header detection
        if entries and entries[0].msgid == "":
            header = entries[0].msgstr
            nplurals, expr = cls._extract_plural_forms_from_header(header)
            catalog._set_plural_forms(nplurals, expr)

        # Normal entries
        for entry in entries:
            if entry.msgid == "":
                continue  # header

            # singular msgstr or fallback to msgid
            singular = entry.msgstr if entry.msgstr else entry.msgid

            msg = Message(
                msgid=entry.msgid,
                singular=singular,
                plural=entry.msgid_plural,
                translations=entry.msgstr_plural.copy(),
            )

            catalog.add_message(msg)

        return catalog

    @staticmethod
    def _extract_plural_forms_from_header(header: str) -> Tuple[int, str]:
        """Extract nplurals and plural expression from header text."""
        nplurals_match = re.search(r"nplurals\s*=\s*(\d+)", header)
        plural_match = re.search(r"plural\s*=\s*([^;]+)", header)

        nplurals = int(nplurals_match.group(1)) if nplurals_match else 2
        expr = plural_match.group(1).strip() if plural_match else "n != 1"

        return nplurals, expr
