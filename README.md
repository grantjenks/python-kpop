# Python k-pop Library

## Overview

`kpoplib` provides a small helper for performing chains of attribute
lookups, indexing, and function calls without having to worry about
exceptions breaking the chain. The `k()` function wraps a value in a
protective "bubble" that records each operation. When an error occurs,
the chain safely returns a default value instead of raising. The
`kpop()` function pops the bubble to retrieve the final result.

## Installation

Install the library from PyPI:

```bash
pip install kpoplib
```

## Usage

```python
from kpop import k, kpop

value = {"a": {"b": [1, 2, 3]}}
bubble = k(value)["a"]["b"][1]
result = kpop(bubble)  # returns 2

# Accessing a missing key or index returns the default (None by default)
missing = k(value)["a"]["missing"][0]
print(kpop(missing))  # prints None
```

Every operation is recorded so you can inspect the history for debugging
via the private `_debug()` method or the `_get_history` helpers.

## Operation History

`Bubble` keeps a log of each attribute access, item lookup and call it
performs. You can view the entire history or the history up until the
first error, making it easier to trace what happened when something goes
wrong.

## License

This project is licensed under the Apache License 2.0. See the
`LICENSE` file for details.
