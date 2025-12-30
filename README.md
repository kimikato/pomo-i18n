# pomo-i18n

**English** | [日本語](README.ja.md)

![Tests](https://github.com/kimikato/pomo-i18n/actions/workflows/tests.yml/badge.svg?branch=main)
[![coverage](https://img.shields.io/codecov/c/github/kimikato/pomo-i18n/main?label=coverage&logo=codecov)](https://codecov.io/gh/kimikato/pomo-i18n)
[![PyPI version](https://img.shields.io/pypi/v/pomo-i18n.svg)](https://pypi.org/project/pomo-i18n/)
[![Python](https://img.shields.io/pypi/pyversions/pomo-i18n.svg)](https://pypi.org/project/pomo-i18n/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**pomo-i18n** is a lightweight Python library for working with GNU gettext translation data,
centered around a practical and explicit `Catalog` model.

Version 0.2.0 focuses on providing a **gettext-compatible**, **in-memory translation catalog**
with a **dict-like API**, while keeping interoperability
with traditional gettext workflows (`.po`, `.mo`, `gettext()`, `ngettext()`).

---

## Overview

`pomo-i18n` is designed for developers who want to:

- Work with gettext translation data **without relying on global state**
- Treat translations as **explicit Python objects**
- Use gettext-compatible behavior while staying idiomatic in Python

At the core of the library is the `Catalog` class -- an in-memory
representation of a gettext message catalog.

A `Catalog`:

- Stores messages keyed by `msgid`
- Treats the header (`msgid == ""`) as first-class data
- Provides a **dict-like interface** compatible with gettext semantics
- Supports plural rules, plural evaluation and caching
- Can be loaded from `.po` / `.mo` files and written back to `.mo`

Unlike the standard gettext module, `pomo-i18n` does not hide state behind
module-level globals. Instead, all translation data lives in explicit `Catalog`
instances, making the behavior predictable, testable, and composable.

---

## Scope and Non-goals

`pomo-i18n` focuses on **explicit, in-memory gettext catalogs**.

It intentionally does NOT provide:

- Global translation state
- Automatic language switching
- Framework-specific integrations (Django, Flask, etc.)

These are expected to be built on top of `Catalog`.

---

## gettext Compatibility

`pomo-i18n` aims to be **behavior-compatible** with GNU gettext where it matters:

- Missing translations fall back to `msgid`
- Header handling follows gettext conventions
- `gettext()` and `ngettext()` APIs are provided
- Plural rules are evaluated according to the gettext specification

At the same time, `pomo-i18n` exposes these concepts through a **clear object model**,
allowing direct inspection and manipulation of translation data.

---

## Installation

```bash
pip install pomo-i18n
```

Requirements:

- Python 3.10+

---

### GNU gettext dependency

pomo-i18n does **not** require GNU gettext at runtime.
Only Python is required.

All runtime operations — loading `.mo` files, evaluating plural rules,
and performing `gettext()` / `ngettext()` lookups — are implemented
entirely in Python.

This makes pomo-i18n usable on platforms such as Windows
without installing external GNU gettext tools.

`.po` files are currently supported as an import format.
Full `.po` -> `.mo` compilation support is planned for a future release.

---

## Quick Start

The central object in `pomo-i18n` is the `Catalog`.

A `Catalog` represents an in-memory gettext message catalog and can be used
much like a Python dictionary.

### Create a Catalog

```python
from pypomo.catalog import Catalog

catalog = Catalog()
```

---

### Dict-like usage

You can assign and retrieve translations using familiar dictionary syntax.

```python
catalog["hello"] = "こんにちは"

print(catalog["hello"])
# -> "こんにちは"
```

If a translation is missing, the `msgid` itself is returned
(gettext-compatible behavior):

```python
print(catalog["missing"])
# -> "missing"
```

The gettext header (`msgid == ""`) is treated as first-class data:

```python
catalog[""] = (
    "Language: ja\n"
    "Plural-Forms: nplurals=2; plural=(n != 1);\n"
)

print(catalog[""])
# -> header string
```

---

### Using `get()`

`Catalog.get()` behaves similarly to `dict.get()` with gettext-compatible fallback behavior:

```python
catalog.get("hello")
# -> CatalogMessage

catalog.get("missing")
# -> "missing"

catalog.get("missing", "fallback")
# -> "fallback"
```

---

### gettext / ngettext APIs

`Catalog` also provides familiar gettext-style APIs:

```python
catalog.gettext("hello")
# -> "こんにちは"

catalog.ngettext("apple", "apples", 1)
# -> "apple"

catalog.ngettext("apple", "apples", 2)
# -> "apples"
```

Plural evaluation follows the `Plural-Forms` rule defined in the catalog header.
If no rule is defined, a gettext-compatible default is used.

---

### Loading and Writing `.po` / `.mo`

A `Catalog` can be created from `.po` (import) or `.mo` files and written back to `.mo` format:

```python
from pypomo.mo.loader import load_mo
from pypomo.mo.writer import write_mo

catalog = load_mo("messages.mo")
write_mo("messages_out.mo", catalog)
```

(See the sections below for details.)

---

## Design Philosophy: Why `Catalog`?

The design of `pomo-i18n` is driven by one core principle:

> **gettext compatibility without hidden global state**

### Problems with the standard `gettext` module

Python’s built-in `gettext` module is powerful, but it comes with trade-offs:

- Translation state is stored in **module-level globals**
- Active language and domain are often implicit
- Testing requires patching or reconfiguring global state
- Inspecting or modifying translation data is difficult

This makes `gettext` awkward in modern Python applications where:

- Explicit dependencies are preferred
- Multiple catalogs may coexist
- Deterministic behavior and testability matter

---

### `Catalog` as an explicit translation object

`pomo-i18n` replaces implicit global state with an explicit object model.

A `Catalog` is:

- A concrete, inspectable Python object
- An in-memory representation of a gettext message catalog
- The single source of truth for:
  - messages
  - header metadata
  - plural rules
  - language information

Instead of asking _“what is the current translation?”_,
you work with _“this specific catalog instance”_.

```python
catalog = Catalog()
catalog["hello"] = "こんにちは"
```

---

### Dict-like API with gettext semantics

A key design goal of `Catalog` is to feel natural to Python users
while remaining faithful to gettext behavior.

Example:

- Missing keys fall back to `msgid`
- The header (`msgid == ""`) is a first-class entry
- No `KeyError` is raised for missing translations
- Plural behavior follows `Plural-Forms` rules

```python
catalog["missing"]
# -> "missing"
```

This mirrors how gettext behaves, but through a familiar
dictionary-style interface.

---

### Separation of concerns

`pomo-i18n` intentionally separates responsibilities:

- `Catalog`
- Owns message data, header state, and plural rules
- `CatalogMessage`
- Represents a single gettext entry (singular, plural, translations)
- `.po` / `.mo` loaders and writers

  Handle file formats, not runtime behavior

This separation allows:

- Clean internal APIs
- Easier refactoring
- Future extensions (e.g. merge strategies, plural dict access)

---

### Designed for extensions, not hidden behavior

`pomo-i18n` is designed around explicit objects and predictable behavior,
rather than hidden state or implicit side effects.

- No implicit language switching
- No hidden registries
- No global translation state

Instead, it provides **building blocks** that can be composed
to fit different application architectures.

This makes the library suitable for:

- CLI tools
- Web frameworks
- Embedded systems
- Testing environments
- Custom i18n pipelines

---

### Summary

In short,

- `Catalog` replaces implicit gettext state with explicit objects
- Dict-like APIs make translation access intuitive
- gettext compatibility is preserved where it matters
- The design favors clarity, predictability, and extensibility

This philosophy shapes all APIs in `pomo-i18n` starting with `Catalog`
and expanding outward.

---

## Dict-like API details (v0.2.0)

`Catalog` provides a **dictionary-like interface** that follows **gettext-compatible semantics**
while remaining explicit and Pythonic.

This API is the **primary interface** of `pomo-i18n` v0.2.0.

---

### `catalog[key]` -- lookup

```python
catalog["hello"]
```

Behavior:

| Condition        | Result                         |
| ---------------- | ------------------------------ |
| key exists       | translated **singular string** |
| key missing      | returns `key` itself           |
| key == `""`      | returns header msgstr          |
| key is not `str` | `TypeError`                    |

Example:

```python
catalog["hello"] = "こんにちは"

catalog["hello"]	# -> "こんにちは"
catalog["missing"]	# -> "missing"
catalog[""]			# -> `header string`
```

Notes:

- Never raises `KeyError`
- Fully compatible with gettext fallback behavior
- Plural forms are **not handled here** (v0.2.0)

---

### `catalog[key] = value` -- assignment

```python
catalog["hello"] = "こんにちは"
```

Behavior:

- `key` must be `str`
- `value` must be `str`
- Creates or replaces a **singular** message
- `key == ""` updates the catalog header

Example:

```python
catalog[""] = "Language: ja\nPlural-Forms: nplurals=2; plural=(n != 1);\n"
```

Notes:

- Plural assignment is intentionally **not supported** in v0.2.0.
- Header assignment updates plural rules if present

---

### `"key" in catalog` -- membership test

```python
"hello" in catalog
```

Behavior:

| Condition      | Result                  |
| -------------- | ----------------------- |
| existing msgid | `True`                  |
| missing msgid  | `False`                 |
| `key == ""`    | `True` if header exists |
| key not `str`  | `False`                 |

Example:

```python
"hello" in catalog
"" in catalog
```

---

### Iteration and Views

```python
for key in catalog:
	...
```

Equivalent to:

```python
catalog.keys()
```

Available views:

```python
catalog.keys()		# KeysView[str]
catalog.values()	# ValuesView[CatalogMessage]
catalog.items()		# ItemsView[str, CatalogMessage]
len(catalog)		# number of messages (including header)
```

---

### `catalog.get(key[, default])`

```python
catalog.get("hello")
catalog.get("hello", default)
```

Behavior (gettext-compatible):

| Condition                     | Result           |
| ----------------------------- | ---------------- |
| key exists                    | `CatalogMessage` |
| key missing, default provided | `default`        |
| key missing, no default       | returns `key`    |
| key not `str`                 | `TypeError`      |

Example:

```python
catalog.get("hello")
# -> CatalogMessage

catalog.get("missing")
# -> "missing"

catalog.get("missing", "fallback")
# -> "fallback"
```

Design notes:

- Unlike `dict.get()`, the no-default case returns `key`
- This mirrors gettext's fallback semantics
- The returned object is **not** a string when a message exists

---

### Deletion is not supported

```python
del catalog["hello"]
```

Always raises:

```python
TypeError
```

Reason:

- gettext catalogs are append/override-oriented
- Explicit deletion is intentionally unsupported

---

### Design rationale

- **No** `KeyError` -- gettext-compatible behavior
- **Explicit message objects** -- avoids hidden state
- **Header as first-class data** -- not a special case
- **Singular-first API** -- plural dict-like API planned for v0.3.0

---

## gettext / ngettext APIs

In addition to its dict-like interface, `Catalog` provides
gettext-compatible translation APIs.

These APIs are intended for **drop-in familiarity** with existing gettext-based
code, while still operating on an explicit `Catalog` interface.

---

### gettext()

```python
catalog.gettext("hello")
# -> "こんにちは"
```

Behavior:

| Situation              | Result                     |
| ---------------------- | -------------------------- |
| Translation exists     | Translated string          |
| Translation not exists | Original `msgid`           |
| `msgid == ""` (header) | Not accessed via gettext() |

This matches standard GNU gettext behavior.

---

### ngettext()

```python
catalog.ngettext("apple", "apples", 1)
# -> "apple"

catalog.ngettext("apple", "apples", 2)
# -> "apples"
```

Behavior:

| Step | Condition                              | Result                                   |
| ---- | -------------------------------------- | ---------------------------------------- |
| 1    | No translation exists                  | `singular` if n == 1, else `plural`      |
| 2    | Translation exists                     | Evaluate plural index via `Plural-Forms` |
| 3    | `msgstr[index]` exists                 | Return that form                         |
| 4    | Index out of range, `msgstr[0]` exists | Fallback to `msgstr[0]`                  |
| 5    | No valid translation form found        | Fallback to translated singular          |
| 6    | Last resort                            | Fallback to original `plural` argument   |

Plural selection follows GNU gettext semantics.

---

### Plural Rules

Plural rules are defined by the `Plural-Forms` header:

```python
Plural-Forms: nplurals=2; plural=(n != 1);
```

| Case                           | Behavior                             |
| ------------------------------ | ------------------------------------ |
| Header contains `Plural-Forms` | Rule is parsed, compiled, and cached |
| Header missing                 | gettext-compatible default is used   |
| Default rule                   | `nplurals=2; plural=(n != 1)`        |

---

### Relationship to the Dict-like API

The dict-like API and gettext-style APIs are **complementary**

| API              | Purpose                                 |
| ---------------- | --------------------------------------- |
| `catalog["key"]` | Simple access (singular only)           |
| `catalog.get()`  | Introspective access to message objects |
| `gettext()`      | gettext-compatible string lookup        |
| `ngettext()`     | Plural-aware gettext-compatible lookup  |

In v0.2.0:

- Dict-like access is **singular-style**
- Plural handling is intentionally explicit via `ngettext()`

---

### Design Notes

| Design Choice             | Rationale                                  |
| ------------------------- | ------------------------------------------ |
| Instance-based API        | No hidden global state                     |
| Explicit `Catalog` object | Deterministic, testable behavior           |
| Separate plural API       | Avoid ambiguous dict-like plural semantics |

---

### Future Direction

| Version | Planned Improvement                      |
| ------- | ---------------------------------------- |
| v0.3.x  | Dict-like plural support                 |
| v0.3.x+ | Closer integration with `CatalogMessage` |

Until then, `ngettext()` remains the canonical plural API.

---

## CatalogMessage Design

`CatalogMessage` is the internal message representation used by `Catalog`.

It corresponds closely to a single gettext entry (`msgid`, `msgstr`, `msgid_plural`, `msgstr[n]`),
but is normalized into a **Python-friendly, immutable-like structure**.

---

### Purpose

`CatalogMessage` exists to:

- Represent a **fully resolved translation unit**
- Separate **parsing concerns** (`POEntry`) from **runtime lookup**
- Provide a stable object model for:

  - dict-like access
  - gettext / ngettext evaluation
  - `.mo` writing

Unlike `POEntry`, `CatalogMessage` is **not a file format model** --
it represents _how translations behave at runtime_.

---

### Structure

```python
@dataclass(slots=True)
class CatalogMessage:
	msgid: str
	singular: str
	plural: str | None
	translations: Dict[int, str]
```

Fields:

| Field          | Meaning                                    |
| -------------- | ------------------------------------------ |
| `msgid`        | Logical key (original untranslated string) |
| `singular`     | Primary translation (never empty)          |
| `plural`       | Plural msgid or None                       |
| `translations` | `{plural_index: translated_string}`        |

---

### Normalization rules

`CatalogMessage` enforces several invariants in `__post_init__`:

- `singular` is **never empty**

  - Falls back to `msgid`

- `plural == ""` is normalized to `None`
- `translations[0]` **always exists**

  - Falls back to `singular`

- Empty plural translations fall back conservatively:

  - index `0` -> `singular`
  - index `n` -> `plural` or `singular`

This guarantees that:

- Lookup code never needs defensive checks
- Missing plural forms degrade safely
- `.mo` writing can assume consistent data

---

### Construction helpers

#### Singular message

```python
CatalogMessage.from_singular(
	msgid="hello",
	msgstr="こんにちは"
)
```

Used by:

- `catalog["key"] = value`
- Simple catalogs without plural support

---

#### Plural message

```python
CatalogMessage.from_plural(
	msgid="apple",
	msgid_plural="apples",
	forms={
		0: "りんご",
		1: "りんごたち",
	},
)
```

Used internally when building from `.po` or `mo` data.

Missing forms are normalized automatically.

---

### Access helpers

```python
msg.as_plain()
```

Returns the singular translation (`translations[0]`)

```python
msg.get_plural(index)
```

Safely retrieves a plural form with fallback.

These helpers are primarily used by:

- `Catalog.__getitem__`
- `Catalog.ngettext`
- `.mo` writer

---

### Immutability model

`CatalogMessage` is **immutable-like** by design:

- Uses `@dataclass(slots=True)`
- No public mutation API
- Treated as replace-on-write inside `Catalog`

This follows:

- Safe reuse across catalogs
- Predictable merge / update semantics
- Efficient caching and plural evaluation

---

### Relationship to other layers

| Layer            | Role                                   |
| ---------------- | -------------------------------------- |
| `POEntry`        | File-format parsing model (`.po`)      |
| `CatalogMessage` | Runtime message representation         |
| `Catalog`        | Lookup, plural evaluation, API surface |

This separation is intentional:

- Parsing (`POEntry`) may change in future versions
- Runtime behavior (`CatalogMessage`) remains stable

---

### Version notes

- v0.2.0 supports **singular-first usage**
- Plural dict-like assignment is planned for v0.3.0
- `CatalogMessage` already supports full plural data

---

## Loading and Writing Translation Files

`pomo-i18n` treats file formats (`.po`, `.mo`) as **serialization layers**
around the central `Catalog` abstraction.

In v0.2.0, `.mo` files are the primary runtime format, while `.po` files are
used as an **import format**.

---

### Loading `.po` Files

Text-based `.po` files can be parsed using `POParser`
and converted into a `Catalog`:

```python
from pypomo.parser.po_parser import POParser
from pypomo.catalog import Catalog

parser = POParser()
entries = parser.parse("messages.po")

catalog = Catalog.from_po_entries(entries)
```

Notes:

- `.po` parsing supports:

  - `msgid`
  - `msgstr`
  - `msgid_plural`
  - `msgstr[n]`
  - multiline strings
  - comments

- Advanced features such as `#, fuzzy`, flags are **collected as comments**
  but **not yet interpreted semantically**
- `.po` files are treated primarily as an **import format** in v0.2.0

---

### Loading `.mo` Files

Binary `.mo` files can be loaded directly into a `Catalog`:

```python
from pypomo.mo.loader import load_mo

catalog = load_mo("messages.mo")
```

This auto:

- Loads all messages into memory
- Parses the header (`msgid == ""`)
- Extracts and evaluates `Plural-Forms`
- Enables immediate use via:
  - `catalog["msgid"]`
  - `catalog.gettext()`
  - `catalog.ngettext()`

---

### Writing `.mo` Files

A `Catalog` can be written back to a gettext-compatible `.mo` file:

```python
from pypomo.mo.writer import write_mo

write_mo("messages_out.mo", catalog)
```

Note:

- Output is fully GNU gettext-compatible
- Header and plural rules are preserved
- Changes made via the dict-like API are reflected in the output
- `.mo` is the recommended runtime/export format

---

### Writing `.po` Files

Writing `.po` files is **not supported v0.2.0**.

Support for `.po` writing and richer metadata handling is planned for
future releases.

---

### Design Notes

- `Catalog` is the single **source of truth**
- `.po` / `.mo` files are **serialization layers**
- No hidden global state
- Explicit, testable, composable translation handling

---

### Roadmap (Related)

Planned improvements in upcoming versions include:

- Refactored `.po` module layout (`pypomo.po.*`)
- Full support for flags (`fuzzy`, etc.)
- `.po` writing support
- Richer merge and update strategies

---

## Roadmap

- v0.3.x
  - Dict-like plural access
  - Refactored `.po` module layout
  - Improved merge strategies

---

## License

MIT License
© 2025 Kiminori Kato
