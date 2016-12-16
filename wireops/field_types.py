# wireops/fieldTypes.py

""" Types for primitive fields. """

# import sys

# from wireops.enum import SimpleEnumWithRepr
#
# #@singleton
# class FieldTypes(SimpleEnumWithRepr):
#
#     def __init__(self):
#         super(FieldTypes, self).__init__( [ \
#             # FIELDS IMPLEMENTED USING VARINTS --
#             ('V_BOOL', 'vBool'),
#             ('V_ENUM', 'vEnum'),
#             # -------------------------------------------------------
#             # NEXT PAIR HAVE BEEN DROPPED, perhaps foolishly; IF SE
#             # ARE ADDED BACK IN, PUT THEM IN THEIR CORRECT ORDER
#             #           ('V_INT32',    'vint32'),  ('_V_INT64',    'vint64'),
#             # -------------------------------------------------------
#             ('V_UINT32', 'vuint32'),
#             ('V_SINT32', 'vsint32'),
#             ('V_UINT64', 'vuint64'),
#             ('V_SINT64', 'vsint64'),
#             # IMPLEMENTED USING B32 -------------
#             ('F_UINT32', 'fuint32'),
#             ('F_SINT32', 'fsint32'),
#             ('F_FLOAT', 'ffloat'),
#             # IMPLEMENTED USING B64 -------------
#             ('F_UINT64', 'fuint64'),
#             ('F_SINT64', 'fsint64'),
#             ('F_DOUBLE', 'fdouble'),
#             # IMPLEMENTED USING LENPLUS --------
#             ('L_strFormING', 'lstring'),
#             ('L_BYTES', 'lbytes'),
#             ('L_MSG', 'lmsg'),
#             # OTHER FIXED LENGTH BYTE SEQUENCES -
#             ('F_BYTES16', 'fbytes16'),
#             ('F_BYTES20', 'fbytes20'),
#             ('F_BYTES32', 'fbytes32'),
#         ])

from enum import IntEnum

# XXX supposedly these should be 1-based


class FieldTypes(IntEnum):
    """ Types for primitive fields. """
    V_BOOL = 0
    V_ENUM = 1
    V_INT32 = 2
    V_INT64 = 3
    V_UINT32 = 4       # skipped in the original version
    V_SINT32 = 5       # skipped in the original version
    V_UINT64 = 6
    V_SINT64 = 7
    F_UINT32 = 8
    F_SINT32 = 9
    F_FLOAT = 10
    F_UINT64 = 11
    F_SINT64 = 12
    F_DOUBLE = 13
    L_STRING = 14
    L_BYTES = 15
    L_MSG = 16
    F_BYTES16 = 17
    F_BYTES20 = 18
    # next two * MUST BE * identical
    F_BYTES32 = 19
    MAX_NDX = 19


class FieldStr(object):
    """ String names for primitive field types. """

    STR_FORM = [
        'vbool',
        'venum',
        'vint32',
        'vint64',
        'vuint32',
        'vsint32',
        'vuint64',
        'vsint64',
        'fuint32',
        'fsint32',
        'ffloat',
        'fuint64',
        'fsint64',
        'fdouble',
        'lstring',
        'lbytes',
        'lmsg',
        'fbytes16',
        'fbytes20',
        'fbytes32',
    ]

    STR2NDX = {}
    for _type in FieldTypes:
        STR2NDX[STR_FORM[_type]] = _type

    @classmethod
    def as_str(cls, ndx):
        """ Given its index, return the string name of the type. """
        return cls.STR_FORM[ndx]

    @classmethod
    def ndx(cls, name):
        """ Given its name in string form, return the index of field type. """
        return cls.STR2NDX[name]

# sys.modules[__name__] = FieldTypes
