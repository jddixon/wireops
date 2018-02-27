# wireops/__init__.py

""" Low-level primitives for transmission of compressed data. """

__version__ = '0.2.10'
__version_date__ = '2018-02-27'


__all__ = ['__version__', '__version_date__', 'WireopsError']


class WireopsError(RuntimeError):
    pass
