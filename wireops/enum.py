# wireops/enum.py

from enum import Enum, IntEnum

__all__ = ['FieldTypes', 'ftype_by_val', 'PrimTypes']


class FieldTypes (Enum):
    """
    X.value[0] is the index, X.valu[1] is its string representation.
    """

    V_BOOL = (0, 'vbool')
    V_ENUM = (1, 'venum')
    # -------------------------------------------------------
    # NEXT PAIR HAVE BEEN DROPPED, perhaps foolishly; IF SE
    # ARE ADDED BACK IN, PUT THEM IN THEIR CORRECT ORDER
    #           V_INT32 =    (, 'vint32'),  ('_V_INT64',    'vint64')
    # -------------------------------------------------------
    V_UINT32 = (2, 'vuint32')
    V_SINT32 = (3, 'vsint32')
    V_UINT64 = (4, 'vuint64')
    V_SINT64 = (5, 'vsint64')
    # IMPLEMENTED USING B32 -------------
    F_UINT32 = (6, 'fuint32')
    F_SINT32 = (7, 'fsint32')
    F_FLOAT = (8, 'ffloat')
    # IMPLEMENTED USING B64 -------------
    F_UINT64 = (9, 'fuint64')
    F_SINT64 = (10, 'fsint64')
    F_DOUBLE = (11, 'fdouble')
    # IMPLEMENTED USING LENPLUS --------
    L_STRING = (12, 'lstring')
    L_BYTES = (13, 'lbytes')
    L_MSG = (14, 'lmsg')
    # OTHER FIXED LENGTH BYTE SEQUENCES -
    F_BYTES16 = (15, 'fbytes16')
    F_BYTES20 = (16, 'fbytes20')
    F_BYTES32 = (17, 'fbytes32')

_ndx = []
for type_ in FieldTypes:
    _ndx.append(type_)


def ftype_by_val(val):
    return _ndx[val]


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
