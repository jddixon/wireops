#!/usr/bin/env python3
# testFixedLen.py

""""
Test encoding and decoding fixed length data types, particularly at
boundary values.
"""

import time
import unittest

from rnglib import SimpleRNG
from wireops.chan import Channel
from wireops.enum import PrimTypes
from wireops.raw import(
    field_hdr_val, read_field_hdr, length_as_varint,
    read_raw_b32, write_b32_field, read_raw_b64, write_b64_field,)

LEN_BUFF = 1024


class TestFixedLen(unittest.TestCase):
    """"
    Test encoding and decoding fixed length data types, particularly at
    boundary values.
    """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    def round_trip32(self, nnn):
        """
        Test writing and reading a 32-bit integer as the first and
        only field in a buffer.
        """
        chan = Channel(LEN_BUFF)

        # -- write 32-bit value -------------------------------------
        field_nbr = 1 + self.rng.next_int16(1024)
        write_b32_field(chan, nnn, field_nbr)
        chan.flip()

        # -- read 32-bit value --------------------------------------
        # first the header (which is a varint) ------------
        (field_type, field_nbr2) = read_field_hdr(chan)
        offset2 = chan.position
        self.assertEqual(PrimTypes.B32, field_type)
        self.assertEqual(field_nbr, field_nbr2)
        self.assertEqual(length_as_varint(field_hdr_val(
            field_nbr, PrimTypes.B32)), offset2)

        # then the varint proper --------------------------
        varint_ = read_raw_b32(chan)
        offset3 = chan.position
        self.assertEqual(nnn, varint_)
        self.assertEqual(offset2 + 4, offset3)

    def round_trip64(self, nnn):
        """
        Test writing and reading a 64-bit integer as the first and
        only field in a buffer
        """
        chan = Channel(LEN_BUFF)

        # -- write 64-bit value -------------------------------------
        field_nbr = 1 + self.rng.next_int16(1024)
        write_b64_field(chan, nnn, field_nbr)
        chan.flip()

#       # DEBUG
#       buf = chan.buffer
#       print "buffer after writing varint field: ",
#       dumpBuffer(buf)
#       # END

        # -- read 64-bit value --------------------------------------
        # first the header (which is a varint) ------------
        (field_type, field_nbr2) = read_field_hdr(chan)
        offset2 = chan.position
        self.assertEqual(PrimTypes.B64, field_type)
        self.assertEqual(field_nbr, field_nbr2)
        self.assertEqual(length_as_varint(field_hdr_val(
            field_nbr, PrimTypes.B64)), offset2)

        # then the varint proper --------------------------
        varint_ = read_raw_b64(chan)
        offset3 = chan.position
        self.assertEqual(nnn, varint_)
        self.assertEqual(offset2 + 8, offset3)

    def test_encode_decode(self):
        """ Test encoding and decoding boundary values. """

        self.round_trip32(0)
        self.round_trip32(42)
        self.round_trip32(0x7f)
        self.round_trip32(0x80)
        self.round_trip32(0x3fff)
        self.round_trip32(0x4000)
        self.round_trip32(0x1fffff)
        self.round_trip32(0x200000)
        self.round_trip32(0xfffffff)
        self.round_trip32(0x10000000)
        self.round_trip32(0xffffffff)

        self.round_trip64(0)
        self.round_trip64(42)
        self.round_trip64(0x7f)
        self.round_trip64(0x80)
        self.round_trip64(0x3fff)
        self.round_trip64(0x4000)
        self.round_trip64(0x1fffff)
        self.round_trip64(0x200000)
        self.round_trip64(0xfffffff)
        self.round_trip64(0x10000000)
        self.round_trip64(0x7ffffffff)
        self.round_trip64(0x800000000)
        self.round_trip64(0x3ffffffffff)
        self.round_trip64(0x40000000000)
        self.round_trip64(0x1ffffffffffff)
        self.round_trip64(0x2000000000000)
        self.round_trip64(0xffffffffffffff)
        self.round_trip64(0x100000000000000)
        self.round_trip64(0x7fffffffffffffff)
        self.round_trip64(0x8000000000000000)
        self.round_trip64(0xffffffffffffffff)

if __name__ == '__main__':
    unittest.main()
