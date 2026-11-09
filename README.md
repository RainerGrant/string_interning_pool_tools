# string_interning_pool_tools

Keeps one canonical `str` object per distinct value so repeated strings share storage.

```python
from string_interning_pool_tools import StringPool

pool = StringPool()
first = pool.intern("GET")
second = pool.intern("GET")
assert first is second  # same object, not just equal

handle = pool.interned("POST")
assert handle.value is pool.intern("POST")
assert "POST" in pool
assert pool.get("DELETE") is None  # get() does not insert
```

## Why this exists

When a program parses a large document it often ends up with thousands of small
strings that repeat — HTTP methods, JSON keys, enum-like tokens. Each distinct
Python object carries its own header and character buffer, so the same five
characters stored ten thousand times costs ten thousand times as much memory as
it needs to. A pool collapses those into one object per distinct value.

The trade-off is explicit: the pool holds a strong reference to every value it
has ever seen. That is the point for token-like data, but it means a pool used
for unbounded, high-cardinality input (user IDs, free text) will grow without
limit. Call `clear()` when a batch is finished, or keep pools scoped to the
phase that needs them.

## What the pool does and does not do

Interning is keyed on the exact value. `"a"`, `"a "`, and `"A"` are three
separate entries; the pool never trims, folds case, or otherwise rewrites what
you hand it. If you want normalisation, do it before calling `intern` — the
pool stays predictable and cheap.

Passing a non-`str` raises `TypeError` rather than coercing with `str()`,
because interning the repr of an arbitrary object is almost never what the
caller meant.

`StringPool` is not thread safe. A pool is expected to be owned by one thread;
if several threads must share one, guard the calls yourself. Adding a lock
would slow the common single-threaded case for a guarantee most callers do not
need.

## API

- `StringPool(initial=None)` — optional iterable of strings to intern up front.
- `intern(value) -> str` — canonical string for `value`, inserting if needed.
- `interned(value) -> InternedString` — wrapper around the canonical string.
- `intern_all(values) -> list[str]` — intern each, preserving input order.
- `get(value) -> str | None` — canonical string if present, else `None`; never inserts.
- `contains(value) -> bool` — membership check.
- `value in pool` — same as `contains`; non-strings are `False`.
- `len(pool)`, `iter(pool)`, `pool.values()` — count, iteration, snapshot tuple.
- `clear()` — drop all entries; existing `InternedString` handles stay valid.

`InternedString` exposes `.value`, compares equal to both plain strings and
other handles with the same text, and hashes like the underlying string, so it
can be used as a dictionary key interchangeably with `str`.

## Running the tests

```
PYTHONPATH=src python -m unittest discover -s tests
```
