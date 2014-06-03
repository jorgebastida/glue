import os
import sys
import contextlib
from StringIO import StringIO


def round_up(value):
    int_value = int(value)
    diff = 1 if value > 0 else -1
    return int_value + diff if value != int_value else int_value


def nearest_fration(value):
    """
    Return the nearest fraction.
    If fraction.Fraction is not available, return a fraction.

    Note: used for Opera CSS pixel-ratio media queries.
    """
    try:
        from fraction import Fraction
        return str(Fraction(value))
    except ImportError:
        return '%i/100' % int(float(value) * 100)


class _Missing(object):
    """ Missing object necessary for cached_property"""
    def __repr__(self):
        return 'no value'

    def __reduce__(self):
        return '_missing'

_missing = _Missing()


class cached_property(object):
    """
    Decorator inspired/copied from mitsuhiko/werkzeug.

    A decorator that converts a function into a lazy property.  The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value"""

    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value


@contextlib.contextmanager
def redirect_stdout(stream=None):
    stream = stream or StringIO()
    sys.stdout = stream
    yield
    sys.stdout = sys.__stdout__
