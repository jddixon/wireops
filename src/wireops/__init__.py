# wireops/__init__.py

""" Low-level primitives for transmission of compressed data. """

__version__ = '0.2.4'
__version_date__ = '2017-07-30'


__all__ = ['__version__', '__version_date__', 'WireopsError']


class WireopsError(RuntimeError):
    pass
