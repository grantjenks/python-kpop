"""Python k-pop library.

This package lets you safely traverse complex expressions by wrapping
values in a protective :class:`~kpop.core.Bubble`. Attribute access,
item lookup and function calls are recorded and any exception is
suppressed. Use :func:`~kpop.core.k` to start a chain and
:func:`~kpop.core.kpop` to retrieve the final value (or a provided
default) once evaluation is complete.
"""

from .core import Bubble, k, kpop

__all__ = ["Bubble", "k", "kpop"]

__version__ = "0.1.0"
