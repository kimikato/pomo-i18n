# src/pypomo/__init__.py

from .gettext import gettext
from .gettext import gettext as _
from .gettext import ngettext, translation

__all__ = [
    "_",
    "gettext",
    "ngettext",
    "translation",
]

__version__ = "0.1.0"
