# py-pomo

**English** | [日本語](README.ja.md)

A minimal, strict-typed internationalization library for Python
supporting `.po` parsing, gettext-compatible APIs, and plural-form evaluation.

`py-pomo` is designed to be lightweight, dependency-free, and suitable for
embedding into applications such as CLI tools, FastAPI backends, or local utilities.

---

## Features

- ✔ Load and parse `.po` files (gettext format)
- ✔ Full plural-forms support (`Plural-Forms:` header)
- ✔ Strict type checking (mypy / Pylance friendly)
- ✔ Simple, Pythonic API: `gettext()`, `ngettext()`, and `translation()`
- ✔ No system dependencies (no libintl)
- ✔ Works on Linux / macOS / Windows

---

## Installation

```sh
pip install py-pomo
```

Or use directly in your project (vendored):

```
src/
 └─ pypomo/
```

---

## Quick Example

```python
from pypomo.gettext import translation

t = translation(
    domain="messages",
    localedir="locales",
    languages=["en"],
)

_ = t.gettext

print(_("Hello"))           # -> "Hello" (from .po)
print(t.ngettext("apple", "apples", 1))   # -> "apple"
print(t.ngettext("apple", "apples", 3))   # -> "apples"
```

Directory structure:

```
locales/
 └─ en/
     └─ LC_MESSAGES/
         └─ messages.po
```

---

## Parsing `.po` Files

`py-pomo` includes a minimal but robust `.po` parser:

- `msgid`, `msgstr`
- plural blocks: `msgid_plural`, `msgstr[n]`
- multiline strings
- comment collection (`#`, `#.`, `#:`, etc.)
- header extraction (`msgid ""`)

Example PO snippet:

```
msgid ""
msgstr ""
"Language: en\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\n"

msgid "apple"
msgid_plural "apples"
msgstr[0] "apple"
msgstr[1] "apples"
```

---

## Plural Forms

`Plural-Forms:` headers are parsed and converted into a Python expression.

Example:

```
Plural-Forms: nplurals=2; plural=(n != 1);

```

Russian example:

```
Plural-Forms: nplurals=3;
 plural=(n%10==1 && n%100!=11 ? 0 :
        n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);
```

The expression is safely compiled into a restricted evaluator.

---

## API Reference

### Catalog

```python
from pypomo.catalog import Catalog
```

Methods:

| Method                          | Description                       |
| ------------------------------- | --------------------------------- |
| `gettext(msgid)`                | Return translated string          |
| `ngettext(singular, plural, n)` | Plural-aware translation          |
| `bulk_update(messages)`         | Merge message dictionaries        |
| `from_po_entries(entries)`      | Build catalog from parsed POEntry |

---

### Top-Level Gettext API

```python
from pypomo.gettext import gettext, ngettext, translation
```

- `gettext(msgid)` -> default catalog lookup
- `ngettext(singular, plural, n)` -> plural-aware lookup
- `translation(domain, localedir, languages)` -> load PO files into a new Catalog

---

## Roadmap

- `.mo` binary loader
- Message merging & locale fallbacks
- Richer comment parsing (`#, fuzzy`, `#.` extracted tags)
- CLI utilities for generating `.pot` files
- Locale auto-detection helpers

---

## License

MIT License
© 2025 Kiminori Kato

---
