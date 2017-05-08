# wireops/enum.py

from enum import IntEnum

__all__ = ['FieldTypes', 'PrimTypes']


# FIELD TYPES =======================================================

FieldTypes = IntEnum('FieldTypes', [
    'V_BOOL', 'V_ENUM', 'V_UINT32', 'V_SINT32', 'V_UINT64',
    'V_SINT64',
    # IMPLEMENTED USING B32 -------------
    'F_UINT32', 'F_SINT32', 'F_FLOAT',
    # IMPLEMENTED USING B64 -------------
    'F_UINT64', 'F_SINT64', 'F_DOUBLE',
    # IMPLEMENTED USING LENPLUS --------
    'L_STRING', 'L_BYTES', 'L_MSG',
    # OTHER FIXED LENGTH BYTE SEQUENCES -
    'F_BYTES16', 'F_BYTES20', 'F_BYTES32'],
    start=0)

_FIELD_SYMBOLS = [
    'vbool', 'venum', 'vuint32', 'vsint32', 'vuint64',
    'vsint64', 'fuint32', 'fsint32', 'ffloat', 'fuint64',
    'fsint64', 'fdouble', 'lstring', 'lbytes', 'lmsg',
    'fbytes16', 'fbytes20', 'fbytes32', ]


@property
def _sym(self):
    """ Return the symbol associated with the member. """
    return _FIELD_SYMBOLS[self.value]


FieldTypes.sym = _sym       # this is now a method of the class

# Add a method which given a symbol returns the associated member.
_FIELD_MAP = {}
for _ in FieldTypes:
    _FIELD_MAP[_.sym] = _


@classmethod
def _from_sym(cls, symbol):
    """ Given a symbol, return the associated member. """
    return _FIELD_MAP[symbol]


FieldTypes.from_sym = _from_sym

# PRIMITIVE TYPES ===================================================


class PrimTypes(IntEnum):

    """
    These are PRIMITIVE types, which determine the number of bytes
    occupied in the buffer; they are NOT data types.
    """
    VARINT = 0  # variable length integer
    PACKED_VARINT = 1  # variable length integer
    B32 = 2  # fixed length, 32 bits
    B64 = 3  # fixed length, 64 bits
    LEN_PLUS = 4  # sequence of bytes preceded by a varint length
    B128 = 5  # fixed length, 128 bits (AES IV length)
    B160 = 6  # fixed length, 160 bits (SHA1 content key)
    B256 = 7  # fixed length, 128 bits (SHA3 content key)
