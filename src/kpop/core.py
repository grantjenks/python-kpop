class Bubble:
    def __init__(
        self, value, default=None, error=None, history=None, error_history=None
    ):
        """
        Initialize the proxy (k-pop bubble).

        Parameters:
            value: The current underlying value.
            default: The value to return when an error is encountered.
            error: The exception encountered (if any).
            history: List of all operations performed.
            error_history: List of operations performed up until the first error (inclusive).
        """
        self._value = value
        self._error = error
        self._default = default
        self._history = history if history is not None else []
        self._error_history = error_history if error_history is not None else []

    def _record(self, op, detail, result, exception):
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
        record = {'op': op, 'detail': detail, 'result': result, 'exception': exception}
        new_history = self._history + [record]
        new_error_history = (
            self._error_history
            if self._error is not None
            else self._error_history + [record]
        )
        return new_history, new_error_history

    def __getattr__(self, attr):
        if self._error is not None:
            new_history, new_error_history = self._record(
                'getattr', attr, None, self._error
            )
            return Bubble(
                None,
                error=self._error,
                default=self._default,
                history=new_history,
                error_history=new_error_history,
            )

        try:
            result = getattr(self._value, attr)
            new_history, new_error_history = self._record('getattr', attr, result, None)
        except Exception as e:
            new_history, new_error_history = self._record('getattr', attr, None, e)
            return Bubble(
                None,
                error=e,
                default=self._default,
                history=new_history,
                error_history=new_error_history,
            )

        return Bubble(
            result,
            default=self._default,
            history=new_history,
            error_history=new_error_history,
        )

    def __getitem__(self, key):
        if self._error is not None:
            new_history, new_error_history = self._record(
                'getitem', key, None, self._error
            )
            return Bubble(
                None,
                error=self._error,
                default=self._default,
                history=new_history,
                error_history=new_error_history,
            )

        try:
            result = self._value[key]
            new_history, new_error_history = self._record('getitem', key, result, None)
        except Exception as e:
            new_history, new_error_history = self._record('getitem', key, None, e)
            return Bubble(
                None,
                error=e,
                default=self._default,
                history=new_history,
                error_history=new_error_history,
            )

        return Bubble(
            result,
            default=self._default,
            history=new_history,
            error_history=new_error_history,
        )

    def __call__(self, *args, **kwargs):
        if self._error is not None:
            new_history, new_error_history = self._record(
                'call', {'args': args, 'kwargs': kwargs}, None, self._error
            )
            return Bubble(
                None,
                error=self._error,
                default=self._default,
                history=new_history,
                error_history=new_error_history,
            )

        try:
            result = self._value(*args, **kwargs)
            new_history, new_error_history = self._record(
                'call', {'args': args, 'kwargs': kwargs}, result, None
            )
        except Exception as e:
            new_history, new_error_history = self._record(
                'call', {'args': args, 'kwargs': kwargs}, None, e
            )
            return Bubble(
                None,
                error=e,
                default=self._default,
                history=new_history,
                error_history=new_error_history,
            )

        return Bubble(
            result,
            default=self._default,
            history=new_history,
            error_history=new_error_history,
        )

    def kpop(self):
        """
        Explicitly resolve the chain (pop the bubble).
        Returns the underlying value if no error occurred, otherwise returns the provided default.
        """
        return self._default if self._error is not None else self._value

    def _get_history(self):
        """Return the complete history of all operations."""
        return self._history

    def _get_error_history(self):
        """
        Return the history up until the first error (inclusive).
        If no error occurred, this will be identical to the complete history.
        """
        return self._error_history

    def _debug(self):
        """Return a dict with the final value, error (if any), complete history, and error history."""
        return {
            'final_value': self._default if self._error is not None else self._value,
            'error': self._error,
            'history': self._history,
            'error_history': self._error_history,
        }

    def __repr__(self):
        if self._error is not None:
            return f'<Bubble Error: {self._error}>'
        return f'<Bubble: {self._value!r}>'


def k(value, default=None):
    """
    Wrap a value in a Bubble (a protective bubble).

    Parameters:
        value: The value to wrap.
        default: The value to return when an error is encountered (default is None).

    The proxy records:
        - history: A list of all operations performed.
        - error_history: The operations up until the first error occurred (inclusive).

    Use pop() to extract the final value.
    """
    return Bubble(value, default=default)


def pop(bubble):
    return bubble.kpop()
