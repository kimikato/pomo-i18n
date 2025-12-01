# py-pomo

**English** | [日本語](README.ja.md)

[![Tests](https://github.com/kimikato/py-pomo/actions/workflows/tests.yml/badge.svg)](https://github.com/kimikato/py-pomo/actions/workflows/tests.yml)
[![PyPI version](https://img.shields.io/pypi/v/py-pomo.svg)](https://pypi.org/project/py-pomo/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A minimal, strict-typed internationalization library for Python
supporting `.po` parsing, gettext-compatible APIs, and a safe, restricted plural-form evaluation.

`py-pomo` is designed to be lightweight, dependency-free, and suitable for
embedding into applications such as CLI tools, FastAPI backends, or local utilities.

---

## Features

- ✔ Load and parse `.po` and `.mo` files (gettext format)
- ✔ Full plural forms support (`Plural-Forms:` header)
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

# Shortcut
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

## Writing `.mo` Files

`py-pomo` includes a small `.mo` writer compatible with GNU gettext.
You can generate `.mo` files from a `Catalog` instance.

### Example: Compile a Catalog into a `.mo` file

```python
from pypomo.catalog import Catalog
from pypomo.mo_writer import write_mo
from pypomo.parser.types import POEntry

entries = [
    POEntry(
        msgid="",
        msgstr=(
            "Language: en\n"
            "Content-Type: text/plain; charset=UTF-8\n"
            "Plural-Forms: nplurals=2; plural=(n != 1);\n"
        ),
        msgid_plural=None,
        msgstr_plural={},
        comments=[],
    ),
    POEntry(
        msgid="Hello",
        msgstr="Hello!",
        msgid_plural=None,
        msgstr_plural={},
        comments=[],
    ),
]

catalog = Catalog.from_po_entries(entries)
write_mo("messages.mo", catalog)
```

### Using the generated `.mo` file

The `.mo` file produced by `py-pomo` can be loaded using Python’s built-in `gettext`:

```python
import gettext

with open("messages.mo", "rb") as f:
    trans = gettext.GNUTranslations(f)

print(trans.gettext("Hello"))  # -> "Hello!"
```

### Features

- Fully compatible with GNU `.mo` binary format
- Automatic fallback header generation (for PO files missing msgid="")
- Supports plural forms (`nplurals`, plural expressions)
- UTF-8 output, no system dependencies

---

## Loading `.mo` Files

`py-pomo` includes a simple and strict `.mo` loader that can read
GNU gettext binary files and convert them into a `Catalog`.

### Example: Load a `.mo` file into a Catalog

```python
from pypomo.mo.loader import load_mo

cat = load_mo("messages.mo")

_ = cat.gettext

print(_("Hello"))       # -> "Hello" (loaded from .mo)
print(cat.ngettext("apple", "apples", 3))
```

### Supported Features

- Fully compatible with GNU `.mo` binary format
- Little-endian header validation (0x9504120E)
- Automatic parsing of the gettext header (`msgid ""`)
- Plural-Forms extraction and plural-rule evaluation
- Correct handling of:
  - singular messages
  - plural messages (`msgid "\x00"` separator)
  - multiple plural forms (`msgstr[n]` → split at `\x00`)

### How it works

1. `read_mo_binary()`

   Reads the binary header and string tables and extracts raw `msgid` / `msgstr` byte arrays.

2. `decode_map_pairs()`

   Converts the byte arrays into structured Python objects:

   - `"single"` entries
   - `"plural-header"` entries

3. `build_catalog_from_pairs()`

   Builds a full `Catalog`, including plural forms from the header.

### When to use `.mo` loading?

Use `.mo` files when:

- You want faster loading time (binary format is much faster than .po parsing)
- Deploying translations in production environments
- Loading translations produced by gettext or msgfmt

If you prefer editable sources, you can continue using `.po` files via `Catalog.from_po_entries()`.

`.mo` loading is completely optional in `py-pomo`.

---

## Benchmarks

Two benchmark suites exist:

### 1. Micro benchmark (timeit)

```sh
make bench
```

### 2. pytest-benchmark

```sh
make bench-pytest
```

### 🏎 Plural Rule Evaluation Benchmark

This library includes optimized plural-rule parsing and evaluation.
The performance is important because plural selection is a hot path in gettext.

#### Environment

- Python 3.10
- macOS Tahoe 26.1 (Apple Silicon, M4)
- pytest-benchmark
- pypomo default settings

#### Backend Comparison

| Backend  | Simple Rule (µs) | Complex Rule (µs) | Notes                                                   |
| -------- | ---------------- | ----------------- | ------------------------------------------------------- |
| **none** | ~2.54            | ~4.83             | No caching. Useful for debugging or comparison.         |
| **weak** | ~2.69            | ~4.89             | Python `dict` cache. Slight overhead on lookup.         |
| **lru**  | ~2.49            | ~4.92             | Fastest overall. Backed by CPython’s C-implemented LRU. |

#### Summary

- **`LRU` cache is the fastest** and recommended for production.
- `weak` cache provides simple in-memory caching.
- `none` is intended for debugging or controlled microbenchmarks.

#### Selecting a Cache Backend

You can select the caching backend via environment variables:

```bash
# Disable caching (debug mode)
export PYPOMO_CACHE=none

# Use weak dict-based cache
export PYPOMO_CACHE=weak

# Use LRU cache (recommended)
export PYPOMO_CACHE=lru

# Change LRU cache size (default: 256)
export PYPOMO_PLURAL_CACHE_SIZE=512
```

You can also override the cache at runtime using:

```python
from pypomo.utils.cache_manager import get_default_cache
cache = get_default_cache(backend="lru")
```

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
