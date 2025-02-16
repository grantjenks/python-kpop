class Bubble:
    def __init__(self, obj, default=None):
        self._obj = obj
        self._default = default

    def __getattr__(self, name):
        try:
            new_obj = getattr(self._obj, name)
        except AttributeError:
            new_obj = self._default
        return Bubble(new_obj, self._default)

    def pop(self):
        return self._obj


def k(obj, default=None):
    return Bubble(obj, default=default)


def pop(bubble):
    return bubble.pop()
