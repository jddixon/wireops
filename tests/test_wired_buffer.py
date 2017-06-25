#!/usr/bin/env python3
# test_wire_buffer.py

""" Test operations on the wire buffer. """

import time
import unittest

from rnglib import SimpleRNG
from wireops.raw import(
    next_power_of_two,
    WireBuffer,
)
# from wireops.raw import *


class TestWireBuffer(unittest.TestCase):
    """ Test operations on the wire buffer. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # actual unit tests #############################################

    def test_pow(self):
        """ Test next_power_of_two function. """
        self.assertRaises(ValueError, next_power_of_two, -1)
        self.assertRaises(ValueError, next_power_of_two, 0)
        self.assertEqual(16, next_power_of_two(15))
        self.assertEqual(16, next_power_of_two(16))

    def test_wire_buffer(self):
        """
        Test operations on a wire buffer, verifying that resultant
        properties are as expected.
        """
        wb_ = WireBuffer(1023)
        self.assertEqual(1024, wb_.capacity)
        self.assertEqual(0, wb_.position)
        self.assertEqual(0, wb_.buffer[0])
        self.assertEqual(wb_.capacity, len(wb_.buffer))

        try:
            wb_.position = wb_.capacity
            self.fail('positioned beyond end of buffer')
        except ValueError:
            pass
        wb_.position = wb_.capacity - 10  # position near end
        wb_.reserve(16)                  # will exceed capacity
        # so the buffer size doubles ...
        self.assertEqual(2 * 1024, wb_.capacity)

    def test_copy(self):
        """ Check copying buffers, maing sure properties are the same. """
        wb_ = WireBuffer(4095)
        self.assertEqual(4096, wb_.capacity)
        wb_.position = 27
        self.assertEqual(27, wb_.position)

        wb_2 = wb_.copy()
        self.assertEqual(4096, wb_2.capacity)
        self.assertEqual(0, wb_2.position)

        self.assertEqual(wb_.buffer, wb_2.buffer)


if __name__ == '__main__':
    unittest.main()
