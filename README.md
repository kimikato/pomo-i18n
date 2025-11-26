# py-pomo

**English** | [日本語](README.ja.md)

A minimal, strict-typed internationalization library for Python
supporting `.po` parsing, gettext-compatible APIs, and a safe, restricted plural-form evaluation.

`py-pomo` is designed to be lightweight, dependency-free, and suitable for
embedding into applications such as CLI tools, FastAPI backends, or local utilities.

---

## Features

- ✔ Load and parse `.po` files (gettext format)
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
