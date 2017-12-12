#!/usr/bin/python3

from enum import IntEnum, auto

import unittest

# Build the basic enumeration ---------------------------------------


class FunnyEnum(IntEnum):
    V_BOOL0 = 0
    V_ENUM1 = auto()
    V_UINT322 = auto()
    V_SINT323 = auto()


# Associate a symbol with each member. ------------------------------
_SYMBOLS = ['vbool', 'venum', 'vuint32', 'vsint32']


@property
def _sym(self):
    """ Return the symbol associated with the member. """
    return _SYMBOLS[self.value]


FunnyEnum.sym = _sym     # we monkey-patch the class

# Add a method which given a symbol returns the associated member ---
_NDX = {}
for _ in FunnyEnum:
    # Map the member's value (an integer) into its symbol.
    _NDX[_.sym] = _


@classmethod
def _from_sym(cls, symbol):
    """ Given a symbol, return the associated member. """
    return _NDX[symbol]


FunnyEnum.from_sym = _from_sym  # monkey-patch this into the class too


class TestFunny(unittest.TestCase):
    """
    Test the mappings from member to symbol and from symbol back to member.
    """

    def test_funny(self):
        self.assertEqual(len(FunnyEnum), 4)
        for member in FunnyEnum:
            print("%-10s %d --> %s" % (
                member.name + ':', member.value, member.sym))

            self.assertEqual(member.sym, _SYMBOLS[member.value])

        for member in FunnyEnum:
            symbol = member.sym
            self.assertEqual(FunnyEnum.from_sym(symbol), member)


if __name__ == '__main__':
    unittest.main()
