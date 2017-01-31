# wireops/typed.py

"""
Operations on typed fields.

Sets up tables holding put, get, and len functions for specific types.
"""

import ctypes
import struct
#import sys

# from wireops.field_types import FieldTypes
from wireops.enum import FieldTypes

from wireops.raw import(
    field_hdr_len, length_as_varint, write_varint_field, read_raw_varint,
    read_raw_b32, write_b32_field, read_raw_b64, write_b64_field,
    read_raw_len_plus, write_len_plus_field, read_raw_b128, write_b128_field,
    read_raw_b160, write_b160_field, read_raw_b256, write_b256_field,
)

__all__ = [
    'encode_sint32', 'decode_sint32',
    'encode_sint64', 'decode_sint64',
    'not_impl',
    'T_PUT_FUNCS', 'T_GET_FUNCS', 'T_LEN_FUNCS',
]


def encode_sint32(value):
    """ Encode a signed int32. """
    val = ctypes.c_int32(0xffffffff & value).value
    # we must have the sign filling in from the left
    varint_ = (val << 1) ^ (val >> 31)
#   # DEBUG
#   print "\nencodeSint32: 0x%x --> 0x%x" % (s, v)
#   # END
    return varint_


def decode_sint32(varint_):
    """ Decode zig-zag:  stackoverflow 2210923. """
    val = (varint_ >> 1) ^ (-(varint_ & 1))
    value = ctypes.c_int32(val).value
#   # DEBUG
#   print "decodeSint32: 0x%x --> 0x%x" % (v, s)
#   # END
    return value


def encode_sint64(value):
    """ Encode a signed int64. """
    varint_ = ctypes.c_int64(0xffffffffffffffff & value).value
    # we must have the sign filling in from the left
    varint_ = (varint_ << 1) ^ (varint_ >> 63)
    return varint_


def decode_sint64(varint_):
    """ Decode a signed int64. """
    varint_ = (varint_ >> 1) ^ (-(varint_ & 1))
    value = ctypes.c_int64(varint_).value
    return value

# DISPATCH TABLES ===================================================


def not_impl(*arg):
    raise NotImplementedError

_NBR_FIELD_TYPES = len(FieldTypes)

T_PUT_FUNCS = [not_impl] * _NBR_FIELD_TYPES
T_GET_FUNCS = [not_impl] * _NBR_FIELD_TYPES
T_LEN_FUNCS = [not_impl] * _NBR_FIELD_TYPES

# puts implemented using varInts --------------------------


def vbool_put(chan, val, nnn):
    if val is True:
        write_varint_field(chan, 1, nnn)
    else:
        write_varint_field(chan, 0, nnn)
# pylint: disable=unsubscriptable-object
T_PUT_FUNCS[FieldTypes.V_BOOL.value] = vbool_put


def venum_put(chan, val, nnn):
    # just handle enums as simple ints for now, but constrain
    # to 16 bits; any sign is uhm mangled
    varint_ = 0xffff & val
    write_varint_field(chan, varint_, nnn)
T_PUT_FUNCS[FieldTypes.V_ENUM.value] = venum_put


def vuint32_put(chan, val, nnn):
    varint_ = 0xffffffff & val
    write_varint_field(chan, varint_, nnn)
T_PUT_FUNCS[FieldTypes.V_UINT32.value] = vuint32_put


def vsint32_put(chan, val, nnn):
    varint_ = encode_sint32(val)
    write_varint_field(chan, varint_, nnn)
T_PUT_FUNCS[FieldTypes.V_SINT32.value] = vsint32_put


def vuint64_put(chan, val, nnn):
    varint_ = 0xffffffffffffffff & val
    write_varint_field(chan, varint_, nnn)
T_PUT_FUNCS[FieldTypes.V_UINT64.value] = vuint64_put


def vsint64_put(chan, val, nnn):
    varint_ = encode_sint64(val)
    write_varint_field(chan, varint_, nnn)
T_PUT_FUNCS[FieldTypes.V_SINT64.value] = vsint64_put

# -- implemented using B32 --------------------------------


def fuint32_put(chan, val, nnn):
    val = ctypes.c_uint32(val).value
    write_b32_field(chan, val, nnn)
T_PUT_FUNCS[FieldTypes.F_UINT32.value] = fuint32_put


def fsint32_put(chan, val, nnn):
    val = ctypes.c_int32(val).value
    write_b32_field(chan, val, nnn)
T_PUT_FUNCS[FieldTypes.F_SINT32.value] = fsint32_put


def ffloat_put(chan, val, nnn):
    # @ means native byte order; < would mean little-endian
    v_rep = struct.pack('@f', val)
    varint_ = struct.unpack('@I', v_rep)[0]
    write_b32_field(chan, varint_, nnn)
T_PUT_FUNCS[FieldTypes.F_FLOAT.value] = ffloat_put

# -- implemented using B64 --------------------------------


def fuint64_put(chan, val, nnn):
    val = ctypes.c_uint64(val).value
    write_b64_field(chan, val, nnn)
T_PUT_FUNCS[FieldTypes.F_UINT64.value] = fuint64_put


def fsint64_put(chan, val, nnn):
    varint_ = ctypes.c_int64(val).value
    write_b64_field(chan, varint_, nnn)
T_PUT_FUNCS[FieldTypes.F_SINT64.value] = fsint64_put


def fdouble_put(chan, val, nnn):
    #val = ctypes.c_double(val).value
    v_rep = struct.pack('@d', val)       # this gives us an 8-byte string
    varint_ = struct.unpack('@L', v_rep)[0]
    write_b64_field(chan, varint_, nnn)
T_PUT_FUNCS[FieldTypes.F_DOUBLE.value] = fdouble_put  # END B64


def l_string_put(chan, val, nnn):
    return write_len_plus_field(chan, val.encode('utf-8'), nnn)
T_PUT_FUNCS[FieldTypes.L_STRING.value] = l_string_put


def lbytes_put(chan, val, nnn):
    return write_len_plus_field(chan, val, nnn)
T_PUT_FUNCS[FieldTypes.L_BYTES.value] = lbytes_put

# XXX NOT GOOD.  val WILL BE DYNAMICALLY DEFINED


def lmsg_put(chan, val, nnn):
    raise NotImplementedError
T_PUT_FUNCS[FieldTypes.L_MSG.value] = lmsg_put


def fbytes16_put(chan, val, nnn):
    return write_b128_field(chan, val, nnn)
T_PUT_FUNCS[FieldTypes.F_BYTES16.value] = fbytes16_put


def fbytes20_put(chan, val, nnn):
    return write_b160_field(chan, val, nnn)
T_PUT_FUNCS[FieldTypes.F_BYTES20.value] = fbytes20_put


def fbytes32_put(chan, val, nnn):
    return write_b256_field(chan, val, nnn)
T_PUT_FUNCS[FieldTypes.F_BYTES32.value] = fbytes32_put  # END B256

# GETS ==============================================================

# varint fields -------------------------------------------


def venum_get(chan):
    return read_raw_varint(chan)
T_GET_FUNCS[FieldTypes.V_ENUM.value] = venum_get


def vbool_get(chan):
    varint_ = read_raw_varint(chan)
    if varint_:
        return True
    else:
        return False
T_GET_FUNCS[FieldTypes.V_BOOL.value] = vbool_get


def vuint32_get(chan):
    return read_raw_varint(chan)
T_GET_FUNCS[FieldTypes.V_UINT32.value] = vuint32_get


def vsint32_get(chan):
    varint_ = read_raw_varint(chan)
    return decode_sint32(varint_)
T_GET_FUNCS[FieldTypes.V_SINT32.value] = vsint32_get


def vuint64_get(chan):
    return read_raw_varint(chan)
T_GET_FUNCS[FieldTypes.V_UINT64.value] = vuint64_get


def vsint64_get(chan):
    varint_ = read_raw_varint(chan)
    return decode_sint64(varint_)
T_GET_FUNCS[FieldTypes.V_SINT64.value] = vsint64_get              # END VAR

# B32 fields ----------------------------------------------


def fuint32_get(chan):
    return read_raw_b32(chan)
T_GET_FUNCS[FieldTypes.F_UINT32.value] = fuint32_get


def fsint32_get(chan):
    return read_raw_b32(chan)
T_GET_FUNCS[FieldTypes.F_SINT32.value] = fuint32_get


def ffloat_get(chan):
    val = read_raw_b32(chan)
    # XXX STUB: cast 32-bit val to double
    return val
T_GET_FUNCS[FieldTypes.F_FLOAT.value] = ffloat_get

# B64 fields ----------------------------------------------


def fuint64_get(chan):
    return read_raw_b64(chan)
T_GET_FUNCS[FieldTypes.F_UINT64.value] = fuint64_get


def fsint64_get(chan):
    return read_raw_b64(chan)
T_GET_FUNCS[FieldTypes.F_SINT64.value] = fuint64_get


def fdouble_get(chan):
    val = read_raw_b64(chan)
    # XXX STUB: cast 64-bit val to double
    return val
T_GET_FUNCS[FieldTypes.F_DOUBLE.value] = fdouble_get

# LEN_PLUS fields -----------------------------------------


def lstring_get(chan):
    b_array = read_raw_len_plus(chan)
    value = b_array.decode('utf-8')
    # DEBUG
    print("lStringGet '%s' => '%s'" % (b_array, value))
    # END
    return value
T_GET_FUNCS[FieldTypes.L_STRING.value] = lstring_get


def lbytes_get(chan):
    return read_raw_len_plus(chan)
T_GET_FUNCS[FieldTypes.L_BYTES.value] = lbytes_get


def lmsg_get(chan):
    # caller must interpret the raw byte array
    return read_raw_len_plus(chan)
T_GET_FUNCS[FieldTypes.L_MSG.value] = lmsg_get

# other fixed-length byte fields --------------------------


def fbytes16_get(chan):
    return read_raw_b128(chan)
T_GET_FUNCS[FieldTypes.F_BYTES16.value] = fbytes16_get


def fbytes20_get(chan):
    return read_raw_b160(chan)
T_GET_FUNCS[FieldTypes.F_BYTES20.value] = fbytes20_get


def fbytes32_get(chan):
    return read_raw_b256(chan)
T_GET_FUNCS[FieldTypes.F_BYTES32.value] = fbytes32_get


# LEN ===============================================================

def vbool_len(val, ndx):
    h_len = field_hdr_len(ndx, FieldTypes.V_BOOL)
    return h_len + 1        # header plus one for value
T_LEN_FUNCS[FieldTypes.V_BOOL.value] = vbool_len

# XXX This needs some thought


def venum_len(val, ndx):
    h_len = field_hdr_len(ndx, FieldTypes.V_ENUM)
    # XXX we constrain val to this range of non-negative ints
    return h_len + length_as_varint(val & 0xffff)
T_LEN_FUNCS[FieldTypes.V_ENUM.value] = venum_len


def vuint32_len(val, ndx):
    h_len = field_hdr_len(ndx, FieldTypes.V_UINT32)
    # XXX we constrain val to this range of non-negative ints
    return h_len + length_as_varint(val & 0xffffffff)
T_LEN_FUNCS[FieldTypes.V_UINT32.value] = vuint32_len


def vsint32_len(val, ndx):
    h_len = field_hdr_len(ndx, FieldTypes.V_SINT32)
    return h_len + length_as_varint(encode_sint32(val))
T_LEN_FUNCS[FieldTypes.V_SINT32.value] = vsint32_len


def vuint64_len(val, ndx):
    h_len = field_hdr_len(ndx, FieldTypes.V_UINT64)
    # XXX we constrain val to this range of non-negative ints
    return h_len + length_as_varint(val & 0xffffffffffffffff)
T_LEN_FUNCS[FieldTypes.V_UINT64.value] = vuint64_len


def vsint64_len(val, ndx):
    h_len = field_hdr_len(ndx, FieldTypes.V_SINT64)
    return h_len + length_as_varint(encode_sint64(val))
T_LEN_FUNCS[FieldTypes.V_SINT64.value] = vsint64_len


def fuint32_len(val, ndx):
    h_len = field_hdr_len(ndx, FieldTypes.F_UINT32)
    return h_len + 4
T_LEN_FUNCS[FieldTypes.F_UINT32.value] = fuint32_len


def fsint32_len(val, ndx):
    h_len = field_hdr_len(ndx, FieldTypes.F_SINT32)
    return h_len + 4
T_LEN_FUNCS[FieldTypes.F_SINT32.value] = fsint32_len


def ffloat_len(val, ndx):
    h_len = field_hdr_len(ndx, FieldTypes.F_FLOAT)
    return h_len + 4
T_LEN_FUNCS[FieldTypes.F_FLOAT.value] = ffloat_len


def fuint64_len(val, ndx):
    h_len = field_hdr_len(ndx, FieldTypes.F_UINT64)
    return h_len + 8
T_LEN_FUNCS[FieldTypes.F_UINT64.value] = fuint64_len


def fsint64_len(val, ndx):
    h_len = field_hdr_len(ndx, FieldTypes.F_SINT64)
    return h_len + 8
T_LEN_FUNCS[FieldTypes.F_SINT64.value] = fsint64_len


def fdouble_len(val, ndx):
    h_len = field_hdr_len(ndx, FieldTypes.F_DOUBLE)
    return h_len + 8
T_LEN_FUNCS[FieldTypes.F_DOUBLE.value] = fdouble_len


def l_string_len(val, ndx):
    h_len = field_hdr_len(ndx, FieldTypes.L_STRING)
    v_len = len(val)
    return h_len + length_as_varint(v_len) + v_len
T_LEN_FUNCS[FieldTypes.L_STRING.value] = l_string_len


def lbytes_len(val, ndx):
    """ Return the length of an lbytes field, with ndx the field number. """
    h_len = field_hdr_len(ndx, FieldTypes.L_BYTES)
    v_len = len(val)
    return h_len + length_as_varint(v_len) + v_len
T_LEN_FUNCS[FieldTypes.L_BYTES.value] = lbytes_len


def lmsg_len(val, ndx):
    """ Return the length of an lmsg field, with ndx the field number. """
    h_len = field_hdr_len(ndx, FieldTypes.L_MSG)
    v_len = val.wire_len
    return h_len + length_as_varint(v_len) + v_len
T_LEN_FUNCS[FieldTypes.L_MSG.value] = lmsg_len


def fbytes16_len(val, ndx):
    """ Return the length of an fbytes16 field, with ndx the field number. """
    h_len = field_hdr_len(ndx, FieldTypes.F_BYTES16)
    return h_len + 16
T_LEN_FUNCS[FieldTypes.F_BYTES16.value] = fbytes16_len


def fbytes20_len(val, ndx):
    """ Return the length of an fbytes20 field, with ndx the field number. """
    h_len = field_hdr_len(ndx, FieldTypes.F_BYTES20)
    return h_len + 20
T_LEN_FUNCS[FieldTypes.F_BYTES20.value] = fbytes20_len


def fbytes32_len(val, ndx):
    """ Return the length of an fbytes32 field, with ndx the field number. """
    h_len = field_hdr_len(ndx, FieldTypes.F_BYTES32)
    return h_len + 32
T_LEN_FUNCS[FieldTypes.F_BYTES32.value] = fbytes32_len
