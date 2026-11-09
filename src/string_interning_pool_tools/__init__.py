"""Public surface of string_interning_pool_tools.

Only the names re-exported here are part of the documented API; the
implementation lives in :mod:`string_interning_pool_tools.core`.
"""

from .core import StringPool, InternedString

__all__ = ["StringPool", "InternedString"]
