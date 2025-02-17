from collections import namedtuple
from typing import Any

Operation = namedtuple('Operation', ['op', 'detail', 'result', 'exception'])


class Bubble:
    __slots__ = ['_value', '_error', '_default', '_history', '_error_history']

    def __init__(self, value: Any, default: Any = None) -> None:
        """
        Initialize the bubble with a value and a default.

        Parameters:
            value: The current underlying value.
            default: The value to return when an error is encountered.
        """
        self._value: Any = value
        self._default: Any = default
        self._error: Exception | None = None
        self._history: list[Operation] = []
        self._error_history: list[Operation] = []

    @classmethod
    def from_bubble(
        cls,
        value: Any,
        default: Any,
        error: Exception | None,
        history: list[Operation],
        error_history: list[Operation],
    ) -> 'Bubble':
        """
        Create a Bubble instance from provided bubble data.

        Parameters:
            value: The current underlying value.
            default: The default value to return on error.
            error: The exception encountered (if any).
            history: list of all operations performed.
            error_history: list of operations performed up until the first error (inclusive).
        """
        obj = cls.__new__(cls)
        obj._value = value
        obj._default = default
        obj._error = error
        obj._history = history
        obj._error_history = error_history
        return obj

    def _record(
        self, op: str, detail: Any, result: Any, exception: Exception | None
    ) -> tuple[list[Operation], list[Operation]]:
        """
        Record an operation.

        Always appends the operation record to the overall history. For the error history,
        if no error has occurred yet, the record is added. Once an error occurs, error_history remains unchanged.

        Parameters:
            op: Operation type (e.g., 'getattr', 'getitem', 'call').
            detail: Details about the operation (attribute name, key, arguments, etc.).
            result: The result if the operation succeeded, or None if not.
            exception: The exception raised, if any.

        Returns:
            A tuple (new_history, new_error_history).
        """
        record = Operation(op, detail, result, exception)
        new_history = self._history + [record]
        new_error_history = (
            self._error_history
            if self._error is not None
            else self._error_history + [record]
        )
        return new_history, new_error_history

    def __getattr__(self, attr: str) -> 'Bubble':
        if self._error is not None:
            new_history, new_error_history = self._record(
                'getattr', attr, None, self._error
            )
            return Bubble.from_bubble(
                None,
                self._default,
                self._error,
                new_history,
                new_error_history,
            )

        try:
            result = getattr(self._value, attr)
            new_history, new_error_history = self._record('getattr', attr, result, None)
        except Exception as exc:
            new_history, new_error_history = self._record('getattr', attr, None, exc)
            return Bubble.from_bubble(
                None,
                self._default,
                exc,
                new_history,
                new_error_history,
            )

        return Bubble.from_bubble(
            result,
            self._default,
            None,
            new_history,
            new_error_history,
        )

    def __getitem__(self, key: Any) -> 'Bubble':
        if self._error is not None:
            new_history, new_error_history = self._record(
                'getitem', key, None, self._error
            )
            return Bubble.from_bubble(
                None,
                self._default,
                self._error,
                new_history,
                new_error_history,
            )

        try:
            result = self._value[key]
            new_history, new_error_history = self._record('getitem', key, result, None)
        except Exception as exc:
            new_history, new_error_history = self._record('getitem', key, None, exc)
            return Bubble.from_bubble(
                None,
                self._default,
                exc,
                new_history,
                new_error_history,
            )

        return Bubble.from_bubble(
            result,
            self._default,
            None,
            new_history,
            new_error_history,
        )

    def __call__(self, *args: Any, **kwargs: Any) -> 'Bubble':
        if self._error is not None:
            new_history, new_error_history = self._record(
                'call', {'args': args, 'kwargs': kwargs}, None, self._error
            )
            return Bubble.from_bubble(
                None,
                self._default,
                self._error,
                new_history,
                new_error_history,
            )

        try:
            result = self._value(*args, **kwargs)
            new_history, new_error_history = self._record(
                'call', {'args': args, 'kwargs': kwargs}, result, None
            )
        except Exception as exc:
            new_history, new_error_history = self._record(
                'call', {'args': args, 'kwargs': kwargs}, None, exc
            )
            return Bubble.from_bubble(
                None,
                self._default,
                exc,
                new_history,
                new_error_history,
            )

        return Bubble.from_bubble(
            result,
            self._default,
            None,
            new_history,
            new_error_history,
        )

    def kpop(self) -> Any:
        """
        Explicitly resolve the chain (pop the bubble).
        Returns the underlying value if no error occurred, otherwise returns the provided default.
        """
        return self._value if self._error is None else self._default

    def _get_history(self) -> list[Operation]:
        """Return the complete history of all operations."""
        return self._history

    def _get_error_history(self) -> list[Operation]:
        """
        Return the history up until the first error (inclusive).
        If no error occurred, this will be identical to the complete history.
        """
        return self._error_history

    def _debug(self) -> dict[str, Any]:
        """Return a dict with the final value, error (if any), complete history, and error history."""
        return {
            'final_value': self._value if self._error is None else self._default,
            'error': self._error,
            'history': self._history,
            'error_history': self._error_history,
        }

    def __repr__(self) -> str:
        if self._error is not None:
            return f'<Bubble Error: {self._error}>'
        return f'<Bubble: {self._value!r}>'


def k(value: Any, default: Any = None) -> Bubble:
    """
    Wrap a value in a Bubble (a protective bubble).

    Parameters:
        value: The value to wrap.
        default: The value to return when an error is encountered (default is None).

    The proxy records:
        - history: A list of all operations performed.
        - error_history: The operations up until the first error occurred (inclusive).

    Use kpop() to extract the final value.
    """
    return Bubble(value, default=default)


def kpop(bubble: Bubble) -> Any:
    return bubble.kpop()
