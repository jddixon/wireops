#!/usr/bin/env python3
# testLenPlus.py

""" Test length-preceded fields and data types. """

import time
import unittest

from rnglib import SimpleRNG
from wireops.chan import Channel
from wireops.enum import PrimTypes
from wireops.raw import(
    field_hdr_val, read_field_hdr, length_as_varint,
    read_raw_len_plus, write_len_plus_field,)

LEN_BUFF = 1024


def dump_buffer(buf):
    """
    Display the contents of a buffer as hex.

    For debugging; not currently used.
    """
    for i in range(16):
        print("0x%02x " % buf[i], end=' ')
    print()


class TestLenPlus(unittest.TestCase):
    """ Test length-preceded fields and data types. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    def round_trip(self, string):
        """
        Verify that a unicode string converted to wire format and then
        back again is the same string.

        This tests writing and reading a string of bytes as the first and
        only field in a buffer.
        """
        chan = Channel(LEN_BUFF)

        # -- write the bytearray ------------------------------------
        field_nbr = 1 + self.rng.next_int16(1024)
        write_len_plus_field(chan, string, field_nbr)
        chan.flip()

#       # DEBUG
#       print("buffer after writing lenPlus field: " + str(chan.buffer))
#       # END

        # -- read the value written ---------------------------------
        # first the header (which is a varint) ------------
        (field_type, field_nbr2,) = read_field_hdr(chan)
        offset2 = chan.position
        self.assertEqual(PrimTypes.LEN_PLUS, field_type)
        self.assertEqual(field_nbr, field_nbr2)
        self.assertEqual(
            length_as_varint(field_hdr_val(field_nbr, PrimTypes.LEN_PLUS)),
            offset2)

        # then the actual value written -------------------
        tstamp = read_raw_len_plus(chan)
        offset3 = chan.position
        self.assertEqual(string, tstamp)
        self.assertEqual(
            offset2 +
            length_as_varint(
                len(string)) +
            len(string),
            offset3)

    def test_encode_decode(self):
        """ Test round tripping utf-8 strings. """
        self.round_trip(''.encode('utf8'))
        self.round_trip('ndx_'.encode('utf8'))
        self.round_trip('should be a random string of bytes'.encode('utf8'))


if __name__ == '__main__':
    unittest.main()
