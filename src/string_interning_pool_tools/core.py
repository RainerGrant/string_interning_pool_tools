"""A string interning pool.

The pool keeps exactly one canonical Python ``str`` object per distinct value.
Repeated values are handed back as the same object, so callers that store many
references to the same logical string pay for the characters once rather than
once per reference.

Design decisions worth stating plainly:

* Interning is keyed on the *value* of the string, not on identity. Two equal
  strings that arrive from different sources collapse to one canonical object.
* The pool never rewrites or normalises the value. ``"a"`` and ``"a "`` are
  distinct entries; callers that want case folding or whitespace trimming must
  do it before interning. This keeps the pool predictable and cheap.
* An ``InternedString`` is a thin wrapper that keeps the canonical string alive
  and exposes it via ``value``. It exists so that callers can hold a reference
  without accidentally re-interning, and so that ``str(interned)`` returns the
  underlying text.
"""

from __future__ import annotations

from typing import Dict, Iterable, Iterator, List, Optional, Tuple

__all__ = ["StringPool", "InternedString"]


class InternedString:
    """A handle to a string owned by a :class:`StringPool`.

    The wrapped value is stored in ``_value`` and is always the canonical
    object for that text inside the pool that produced it. Equality and hashing
    delegate to the underlying string so that an ``InternedString`` can be used
    interchangeably with a plain ``str`` in sets and dictionaries.
    """

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(
                "InternedString requires a str, got %r" % (type(value).__name__,)
            )
        self._value = value

    @property
    def value(self) -> str:
        """The canonical string object."""

        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return "InternedString(%r)" % (self._value,)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, InternedString):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)

    def __len__(self) -> int:
        return len(self._value)

    def __contains__(self, item: object) -> bool:
        return item in self._value

    def __iter__(self) -> Iterator[str]:
        return iter(self._value)


class StringPool:
    """Stores one canonical copy of each distinct string value.

    The pool keeps its own dictionary of canonical strings. ``intern`` returns
    the stored object; ``interned`` wraps it in an :class:`InternedString` for
    callers that prefer a distinct handle type.

    The pool is not thread safe. A single pool is expected to be owned by one
    thread; if several threads must share one, guard it with a lock at the call
    site. Documenting that here is deliberate: silently adding a lock would
    make the common single-threaded case slower for no benefit.
    """

    __slots__ = ("_pool",)

    def __init__(self, initial: Optional[Iterable[str]] = None) -> None:
        self._pool: Dict[str, str] = {}
        if initial is not None:
            for item in initial:
                self.intern(item)

    def intern(self, value: str) -> str:
        """Return the canonical string object equal to ``value``.

        ``value`` must be a ``str``. Non-string input raises ``TypeError``
        rather than being coerced, because silently calling ``str()`` on an
        arbitrary object would intern its repr and surprise callers.
        """

        if not isinstance(value, str):
            raise TypeError(
                "StringPool.intern requires a str, got %r" % (type(value).__name__,)
            )
        existing = self._pool.get(value)
        if existing is not None:
            return existing
        self._pool[value] = value
        return value

    def interned(self, value: str) -> InternedString:
        """Return an :class:`InternedString` wrapping the canonical value."""

        return InternedString(self.intern(value))

    def intern_all(self, values: Iterable[str]) -> List[str]:
        """Intern every value and return canonical strings in input order."""

        return [self.intern(value) for value in values]

    def get(self, value: str) -> Optional[str]:
        """Return the canonical string for ``value``, or ``None`` if absent.

        Unlike ``intern`` this does not add a new entry. It is the read-only
        probe used by callers that only want to check membership.
        """

        return self._pool.get(value)

    def contains(self, value: str) -> bool:
        """Whether ``value`` is already present in the pool."""

        return value in self._pool

    def __contains__(self, value: object) -> bool:
        return isinstance(value, str) and value in self._pool

    def __len__(self) -> int:
        return len(self._pool)

    def __iter__(self) -> Iterator[str]:
        return iter(self._pool)

    def values(self) -> Tuple[str, ...]:
        """A snapshot tuple of the canonical strings currently held."""

        return tuple(self._pool.values())

    def clear(self) -> None:
        """Drop every entry. Existing ``InternedString`` handles stay valid."""

        self._pool.clear()
