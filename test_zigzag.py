#!/usr/bin/env python3
# test_zigzag.py

""" Test the zig-zag encoding used with some varints. """

import time
import unittest
import ctypes

from rnglib import SimpleRNG
# from wireops.raw import *
from wireops.typed import(
    encode_sint32, encode_sint64, decode_sint32, decode_sint64)


class TestTFReader(unittest.TestCase):
    """ Test the zig-zag encoding used with some varints. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

#   def dump_buffer(self, buf):
#       for b_val in buf:
#           print("0x%02x " % b_val, end=' ')
#       print()

    def test_int32s(self):
        """
        Verify that certain 32-bit values can be treated as either
        signed or unsigned integers by the CPython interpreter.
        """
        value = 0xffffffff
        s32 = ctypes.c_int32(value).value
        self.assertEqual(-1, s32)
        u32 = ctypes.c_uint32(value).value
        self.assertEqual(256 * 256 * 256 * 256 - 1, u32)

        ndx_ = 0xffffff00
        value = ~ndx_
        s32 = ctypes.c_int32(value).value
        self.assertEqual(0xff, s32)
        u32 = ctypes.c_uint32(value).value
        self.assertEqual(0xff, u32)

    def test_int64s(self):
        """
        Verify that 0xffffffffffffffff can be seen by the Python
        interpreter as either a signed or unsigned integer.
        """
        val = 0xffffffffffffffff
        # 'value' converts back to Python type
        s64 = ctypes.c_int64(val).value
        self.assertEqual(-1, s64)
        u64 = ctypes.c_uint64(val).value
        self.assertEqual(
            256 * 256 * 256 * 256 * 256 * 256 * 256 * 256 - 1, u64)

    def do_round_trip32(self, value):
        """
        Round trip a particular 32-bit value, verifying that encoding
        and then decoding produce the same value.
        """
        zzz = encode_sint32(value)
        value2 = decode_sint32(zzz)
        self.assertEqual(value, value2)

    def do_round_trip64(self, value):
        """
        Round trip a particular 64-bit value, verifying that encoding
        and then decoding produce the same value.
        """
        zzz = encode_sint64(value)
        value2 = decode_sint64(zzz)
        self.assertEqual(value, value2)

    def test_zz32(self):
        """ Test round-tripping interesting 32-bit values. """
        self.do_round_trip32(0)
        self.do_round_trip32(-1)
        self.do_round_trip32(1)
        self.do_round_trip32(-2)
        self.do_round_trip32(2)

        # XXX THIS VALUE CAUSES AN ERROR IN testTFWriter (returns -96)
        self.do_round_trip32(-192)

        # XXX should do a few random numbers here instead
        self.do_round_trip32(-15379)
        self.do_round_trip32(15379)

        self.do_round_trip32(-128 * 256 * 256 * 256)
        self.do_round_trip32(128 * 256 * 256 * 256 - 1)

        # XXX need to also verify that sensible truncation takes place
        # if value doesn't actually fit in an int32

    def test_zz64(self):
        """ Test round-tripping interesting 64-bit values. """
        self.do_round_trip64(0)
        self.do_round_trip64(-1)
        self.do_round_trip64(1)
        self.do_round_trip64(-2)
        self.do_round_trip64(2)

        self.do_round_trip64(-128 * 256 * 256 * 256 * 256 * 256 * 256 * 256)
        self.do_round_trip64(128 * 256 * 256 * 256 * 256 * 256 * 256 * 256 - 1)

if __name__ == '__main__':
    unittest.main()
