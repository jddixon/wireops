# fieldz/raw.py

"""
Functions supporting the low-level manipulation of fields on the wire.
"""
import ctypes       # XXX
from wireops import WireopsError
from wireops.enum import FieldTypes, PrimTypes

__all__ = [
    'field_hdr_val', 'read_field_hdr', 'field_hdr_len',
    'hdr_field_nbr', 'hdr_ptype',
    'length_as_varint', 'write_varint_field',
    'read_raw_varint', 'write_raw_varint',
    'read_raw_b32', 'write_b32_field',
    'read_raw_b64', 'write_b64_field',
    'read_raw_len_plus', 'write_len_plus_field',
    'read_raw_b128', 'write_b128_field',
    'read_raw_b160', 'write_b160_field',
    'read_raw_b256', 'write_b256_field',
    # -- methods --------------------------------------------
    'next_power_of_two',
    # -- classes --------------------------------------------
    'WireBuffer',
]

# FIELD HEADERS #####################################################


def field_hdr_val(ndx, ptype):
    """
    Given the field number and its primitive type, return the value of
    the header.

    Primitive types include PrimTypes.VARINT, PrimTypes.PACKED_VARINT, etc.

    It would be prudent but slower to validate the parameters.
    """
    # DEBUG
    #   print "ndx = %u, t = %u, header is 0x%x" % (n, t, (n << 3) | t)
    # END
    return (ndx << 3) | ptype.value


def field_hdr_len(ndx, ftype):
    """
    Return the length of a header, given the field number ndx and its
    field type.

    The 'type' is FieldType.value.

    XXX THE NEXT CALCULATION IS AN ERROR.  There are currently 8 PrimTypes
    but 18 FieldTypes.
    """
    fndx = ftype.value
    # pylint is a bit thick
    # pylint: disable=unsubscriptable-object
    # pylint: disable=redefined-variable-type
    if fndx < FieldTypes.F_UINT32.value:
        ptype = PrimTypes.VARINT
    elif fndx < FieldTypes.F_UINT64.value:
        ptype = PrimTypes.B32
    elif fndx < FieldTypes.L_STRING.value:
        ptype = PrimTypes.B64
    elif fndx < FieldTypes.F_BYTES16.value:
        ptype = PrimTypes.LEN_PLUS
    elif fndx == FieldTypes.F_BYTES16.value:
        ptype = PrimTypes.B128
    elif fndx == FieldTypes.F_BYTES20.value:
        ptype = PrimTypes.B160
    elif fndx == FieldTypes.F_BYTES32.value:
        ptype = PrimTypes.B256
    else:
        raise WireopsError("FieldType has invalid index %d" % fndx)

    return length_as_varint(field_hdr_val(ndx, ptype))


def hdr_field_nbr(header):
    """ Given a header, extract and return the field number. """
    return header >> 3


def hdr_ptype(header):
    """
    Given a header exract and return the primitive header type.

    Here the 'type' is the index of the field type in FieldTypes.
    """
    return header & 7


def read_field_hdr(chan):
    """ Return a field header (index plus primitive type) from a channel."""

    hdr = read_raw_varint(chan)
    ptype = hdr_ptype(hdr)      # this is the primitive field type
    field_nbr = hdr_field_nbr(hdr)
    return (ptype, field_nbr)

# VARINTS ###########################################################


def length_as_varint(value):
    """
    Return the number of bytes occupied by an unsigned int.
    caller is responsible for assuring that v is in fact properly
    cast as unsigned occupying no more space than an int64 (and
    so no more than 10 bytes).
    """
    # pylint: disable=too-many-return-statements
    if value < (1 << 7):
        return 1
    elif value < (1 << 14):
        return 2
    elif value < (1 << 21):
        return 3
    elif value < (1 << 28):
        return 4
    elif value < (1 << 35):
        return 5
    elif value < (1 << 42):
        return 6
    elif value < (1 << 49):
        return 7
    elif value < (1 << 56):
        return 8
    elif value < (1 << 63):
        return 9
    else:
        return 10


def read_raw_varint(chan):
    """ Read a bare varint from a channel. """

    buf = chan.buffer
    offset = chan.position
    value = 0
    ndx_ = 0
    while True:
        if offset >= len(buf):
            raise ValueError("attempt to read beyond end of buffer")
        next_byte = buf[offset]
        offset += 1

        sign = next_byte & 0x80
        next_byte = next_byte & 0x7f
        next_byte <<= (ndx_ * 7)
        value |= next_byte
        ndx_ += 1

        if sign == 0:
            break
    chan.position = offset
    return value


def write_raw_varint(chan, string):
    """ Write a simple varint to the channel. """

    buf = chan.buffer
    offset = chan.position
    # all varints are construed as 64 bit unsigned numbers
    value = ctypes.c_uint64(string).value
#   # DEBUG
#   print "entering writeRaw: will write 0x%x at offset %u" % ( v, offset)
#   # END
    len_ = length_as_varint(value)
    if offset + len_ > len(buf):
        raise ValueError("can't fit varint of length %u into buffer" % len_)
    while True:
        buf[offset] = (value & 0x7f)
        offset += 1
        value >>= 7
        if value == 0:
            chan.position = offset   # next unused byte
            break
        else:
            buf[offset - 1] |= 0x80


def write_varint_field(chan, varint_, nnn):
    """
    Write a header followed by a varint to a channel.

    The header is the field number << 3 ORed with 0, PrimTypes.VARINT.
    """
    hdr = field_hdr_val(nnn, PrimTypes.VARINT)
    write_raw_varint(chan, hdr)
#   # DEBUG
#   print "header was 0x%x; writing value 0x%x at offset %u" % (
#                                               hdr, v, chan.position)
#   # END
    write_raw_varint(chan, varint_)

# 32- AND 64-BIT FIXED LENGTH FIELDS ################################


def read_raw_b32(chan):
    """
    Read a 4-byte value from a channel.

    buf construed as array of unsigned bytes.
    """
    buf = chan.buffer
    offset = chan.position
    # XXX verify buffer long enough
    value = buf[offset]
    offset += 1         # little-endian
    value |= buf[offset] << 8
    offset += 1
    value |= buf[offset] << 16
    offset += 1
    value |= buf[offset] << 24
    offset += 1
    chan.position = offset
    return value


def write_raw_b32(chan, value):
    """ Write a simple 4-byte value to a channel. """
    buf = chan.buffer
    offset = chan.position
    buf[offset] = 0xff & value
    value >>= 8
    offset += 1
    buf[offset] = 0xff & value
    value >>= 8
    offset += 1
    buf[offset] = 0xff & value
    value >>= 8
    offset += 1
    buf[offset] = 0xff & value
    offset += 1
    chan.position = offset


def write_b32_field(chan, value, ndx):
    """ Write a header followed by a 4-byte value to a channel. """
    hdr = field_hdr_val(ndx, PrimTypes.B32)
    write_raw_varint(chan, hdr)
    write_raw_b32(chan, value)


def read_raw_b64(chan):
    """
    Read a simple 8-byte value from a channel.

    buf construed as array of unsigned bytes
    """
    buf = chan.buffer
    offset = chan.position
    # XXX verify buffer long enough
    value = buf[offset]
    offset += 1         # little-endian
    value |= buf[offset] << 8
    offset += 1
    value |= buf[offset] << 16
    offset += 1
    value |= buf[offset] << 24
    offset += 1
    value |= buf[offset] << 32
    offset += 1
    value |= buf[offset] << 40
    offset += 1
    value |= buf[offset] << 48
    offset += 1
    value |= buf[offset] << 56
    offset += 1
    chan.position = offset
    return value


def write_raw_b64(chan, value):
    """ Write an 8-byte value to a channel. """
    # XXX verify buffer long enough
    buf = chan.buffer
    offset = chan.position
    buf[offset] = 0xff & value
    value >>= 8
    offset += 1
    buf[offset] = 0xff & value
    value >>= 8
    offset += 1
    buf[offset] = 0xff & value
    value >>= 8
    offset += 1
    buf[offset] = 0xff & value
    value >>= 8
    offset += 1
    buf[offset] = 0xff & value
    value >>= 8
    offset += 1
    buf[offset] = 0xff & value
    value >>= 8
    offset += 1
    buf[offset] = 0xff & value
    value >>= 8
    offset += 1
    buf[offset] = 0xff & value
    offset += 1
    chan.position = offset


def write_b64_field(chan, value, ndx):
    """ Write a header and an 8-byte value to a channel. """
    hdr = field_hdr_val(ndx, PrimTypes.B64)
    write_raw_varint(chan, hdr)
    write_raw_b64(chan, value)

# VARIABLE LENGTH FIELDS ############################################


def read_raw_len_plus(chan):
    """ Read a length-preceded value from a channel. """

    # read the varint len
    len_ = read_raw_varint(chan)
    buf = chan.buffer
    offset = chan.position

#   # DEBUG
#   print "readRawLenPlus: length of text is %d bytes" % len_
#   # END

    # then read n actual bytes
    string = []
    count = 0
    while count < len_:
        string.append(buf[offset])
        count += 1
        offset += 1
    chan.position = offset
    return bytearray(string)


def write_raw_bytes(chan, bytes_):
    """ bytes a byte array """
    buf = chan.buffer
    offset = chan.position
    # XXX CHECK LEN OFFSET

    # DEBUG
    # print("writeRawBytes: type(bytes) is ", type(bytes_))
    # END

    for b_val in bytes_:
        buf[offset] = int(b_val)
        offset += 1
#   # DEBUG
#   print("wrote '%s' as %u raw bytes" % (str(bytes_), len(bytes_)))
#   # END
    chan.position = offset

# XXX 2012-12-11 currently used only in one place


def write_field_hdr(chan, field_nbr, prim_type):
    """ Write the field header for a primitive type. """
    hdr = field_hdr_val(field_nbr, prim_type)
    write_raw_varint(chan, hdr)


def write_len_plus_field(chan, string, ndx):
    """
    Write a field, a header followed by length-preceded value.

    s is a bytearray or string.
    """
    write_field_hdr(chan, ndx, PrimTypes.LEN_PLUS)
    # write the length of the byte array --------
    write_raw_varint(chan, len(string))

    # now write the byte array itself -----------
    write_raw_bytes(chan, string)

# LONGER FIXED-LENGTH BYTE FIELDS ===================================


def read_raw_b128(chan):
    """
    Read a 16-byte value from a channel.

    buf construed as array of unsigned bytes
    """
    # XXX verify buffer long enough
    buf = chan.buffer
    offset = chan.position
    string = []
    for i in range(16):
        string.append(buf[offset + i])
    offset += 16
    chan.position = offset
    return bytearray(string)


def write_raw_b128(chan, value):
    """
    Write a 16-byte value to a channel.

    value is a bytearray or string.
    """
    buf = chan.buffer
    offset = chan.position
    for i in range(16):
        # this is a possibly unnecessary cast
        buf[offset] = 0xff & value[i]
        offset += 1
    chan.position = offset


def write_b128_field(chan, value, ndx):
    """ Write a header and 16-byte value to a channel.  """
    hdr = field_hdr_val(ndx, PrimTypes.B128)
    write_raw_varint(chan, hdr)
    write_raw_b128(chan, value)                  # GEEP


def read_raw_b160(chan):
    """
    Read a 20 byte value from a channel.

    buf construed as array of unsigned bytes.
    """
    # XXX verify buffer long enough
    buf = chan.buffer
    offset = chan.position
    string = []
    for i in range(20):
        string.append(buf[offset + i])
    offset += 20
    chan.position = offset
    return bytearray(string)


def write_raw_b160(chan, value):
    """
    Write a 20-byte value to a channel.

    v is a bytearray or string.
    """
    buf = chan.buffer
    offset = chan.position
    for i in range(20):
        buf[offset] = value[i]
        offset += 1
    chan.position = offset


def write_b160_field(chan, value, ndx):
    """ Write a header and 20-byte value to this ndx. """
    hdr = field_hdr_val(ndx, PrimTypes.B160)
    write_raw_varint(chan, hdr)
    write_raw_b160(chan, value)                  # GEEP


def read_raw_b256(chan):
    """ buf construed as array of unsigned bytes """
    # XXX verify buffer long enough
    buf = chan.buffer
    offset = chan.position
    string = []
    for i in range(32):
        string.append(buf[offset + i])
    offset += 32
    chan.position = offset
    return bytearray(string)


def write_raw_b256(chan, value):
    """ v is a bytearray or string """
    buf = chan.buffer
    offset = chan.position
    # DEBUG
    # print "DEBUG: writeRawB256 datum len is %s" % len(v)
    # END
    for i in range(32):
        # print "DEBUG:    v[%u] = %s" % (i, binascii.b2a_hex(v[i]))
        buf[offset] = value[i]
        offset += 1
    chan.position = offset


def write_b256_field(chan, value, ndx):
    """ Write a 32-byte value to a channel. """
    hdr = field_hdr_val(ndx, PrimTypes.B256)
    write_raw_varint(chan, hdr)
    write_raw_b256(chan, value)

# PRIMITIVE FIELD NAMES =============================================


# class PrimFields(object):
#   """ lower-level primitive field types """

#   _P_VARINT = 0
#   _P_B32 = 1     # 32 bit fields
#   _P_B64 = 2     # 64 bit fields
#   _P_LEN_PLUS = 3     # varint len followed by that many bytes
#   # the following can be implemented in terms of _P_LEN_PLUS
#   _P_B128 = 4    # fixed length string of 16 bytes
#   _P_B160 = 5    # fixed length string of 20 bytes
#   _P_B256 = 6    # fixed length string of 32 bytes

#   _MAX_TYPE = _P_B256

#   # none of these (pVarint..pB256) is currently used
#   @property
#   def pVarint(clz):       return clz._P_VARINT
#   @property
#   def pB32(clz):          return clz._P_B32
#   @property
#   def pB64(clz):          return clz._P_B64
#   @property
#   def pLenPlus(clz):      return clz._P_LenPlus
#   @property
#   def pB128(clz):         return clz._P_B128
#   @property
#   def pB160(clz):         return clz._P_B160
#   @property
#   def pB256(clz):         return clz._P_B256

#   _names = {}
#   _names[_P_VARINT] = 'pVarint'
#   _names[_P_B32] = 'pB32'
#   _names[_P_B64] = 'pB64'
#   _names[_P_LEN_PLUS] = 'pLenPlus'
#   _names[_P_B128] = 'pB128'
#   _names[_P_B160] = 'pB160'
#   _names[_P_B256] = 'pB256'

#   @classmethod
#   def name(cls, ndx):
#       """ Return the name of the primitive type with this index. """
#       if ndx is None or ndx < 0 or FieldTypes.MAX_NDX < ndx:
#           raise ValueError('no such field type: %s' + str(ndx))
#       return cls._names[ndx]

# -- WireBuffer -----------------------------------------------------


def next_power_of_two(nnn):
    """
    If n is a power of two, return n.  Otherwise return the next
    higher power of 2.
    See eg http://acius2.blogspot.com/2007/11/calculating-next-power-of-2.html
    """
    if nnn < 1:
        raise ValueError("nextPowerOfTwo: %s < 1" % str(nnn))
    nnn = nnn - 1
    nnn = (nnn >> 1) | nnn
    nnn = (nnn >> 2) | nnn
    nnn = (nnn >> 4) | nnn
    nnn = (nnn >> 8) | nnn
    nnn = (nnn >> 16) | nnn

    # added 2016-12-15
    nnn = (nnn >> 32) | nnn
    # XXX RAISE if nnn > 2^32
    return nnn + 1


class WireBuffer(object):
    """
    A buffer handling data holding binary data to be put on the wire.

    The capacity of the buffer will be a power of two.
    """

    __slots__ = ['_buffer', '_capacity', '_limit', '_position', ]

    def __init__(self, nnn=1024, buffer=None):
        """
        Initialize the object.  If a buffer is specified, use it.
        Otherwise create one.  The resulting buffer will have a
        capacity which is the next power of 2 greater than or equal to nnn.
        """
        if buffer:
            self._buffer = buffer
            buf_size = len(buffer)
            if nnn < buf_size:
                nnn = buf_size
            nnn = next_power_of_two(nnn)
            # DANGER: buffer capacities of cloned buffers can get out of sync
            if nnn > buf_size:
                more = bytearray(nnn - buf_size)
                self.buffer.extend(more)
        else:
            nnn = next_power_of_two(nnn)
            # allocate and initialize the buffer; init probably a waste of time
            self._buffer = bytearray(nnn)

        self._capacity = nnn
        self._limit = nnn
        self._position = 0

    def copy(self):
        """
        Returns a copy of this WireBuffer using the same underlying
        bytearray.
        """
        return WireBuffer(len(self._buffer), self._buffer)

    @property
    def buffer(self):
        """ Return the buffer used to store data being put on the wire. """
        return self._buffer

    @property
    def position(self):
        """ Return the current position in the buffer. """
        return self._position

    @position.setter
    def position(self, offset):
        """ Set the current position in the buffer. """
        if offset < 0:
            raise ValueError('position cannot be negative')
        if offset >= len(self._buffer):
            raise ValueError('position cannot be beyond capacity')
        self._position = offset

    @property
    def limit(self):
        """
        Return the current limit of the buffer.

        0 <= limit <= capacity.
        """
        return self._limit

    @limit.setter
    def limit(self, offset):
        """ Set the value of the buffer's limit. """
        if offset < 0:
            raise ValueError('limit cannot be set to a negative')
        if offset < self._position:
            raise ValueError(
                "limit can't be set to less than current position")
        if offset > self._capacity:
            raise ValueError('limit cannot be beyond capacity')
        self._limit = offset

    @property
    def capacity(self):
        """ Return the capacity of the buffer. """
        return len(self._buffer)

    def reserve(self, k):
        """
        We need to add k more bytes; if the buffer isn't big enough,
        resize it.
        """
        if k < 0:
            raise ValueError(
                "attempt to increase WireBuffer size by negative number")
        if self._position + k >= self._capacity:
            # wildly inefficient, I'm sure
            more = bytearray(self._capacity)
            self._buffer.extend(more)
            self._capacity *= 2
