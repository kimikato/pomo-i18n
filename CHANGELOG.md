# Changelog

All notable changes to this project will be documented in this file.

This project follows [Semantic Versioning](https://semver.org/).

---

## [0.2.0] - 2025-12-31

[GitHub Release](https://github.com/kimikato/pomo-i18n/releases/tag/v0.2.0)

> Note
> Versions prior to v0.2.0 were experimental and are not considered stable.
> v0.2.0 is the first release with a stabilized public API and documented design philosophy.

### Added

- Introduced `Catalog` as the central, explicit gettext catalog object
- Dict-like API with gettext-compatible fallback semantics
- `gettext()` and `ngettext()` APIs operating on `Catalog`
- `CatalogMessage` as a normalized runtime message representation
- `.mo` file loading and writing (GNU gettext compatible)
- `.po` file parsing as an import format
- Parsing, evaluation, and caching of `Plural-Forms`
- Header (`msgid == ""`) treated as first-class catalog data
- Comprehensive test coverage for core catalog behavior

### Design

- Explicit object-based translation model (no global state)
- Clear separation between runtime behavior and file format layers
- Singular-first dict-like API design
- Serialization layers (`.po`, `.mo`) isolated from runtime logic
- Designed for extension without implicit or hidden behavior

### Not Supported

- Writing `.po` files
- Dict-like plural assignment
- Global or implicit translation state
- Automatic language switching

---

## [Unreleased]

### Planned

- Dict-like plural access (v0.3.x)
- Refactored `.po` module layout (`pypomo.po.*`)
- Support for `.po` file writing
- Semantic handling of flags such as `fuzzy`
- Improved merge and update strategies
