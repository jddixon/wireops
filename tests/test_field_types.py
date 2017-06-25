#!/usr/bin/env python3
# testFieldTypes.py

""" Exercise the FieldTypes class. """

import time
import unittest

from wireops.enum import FieldTypes

from wireops import raw, typed
from rnglib import SimpleRNG


class TestFieldTypes(unittest.TestCase):
    """
    Actually tests the method used for instantiating and importing
    an instance of the FieldTypes class.
    """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    def test_new_fieldtypes(self):
        """
        Test the new definition of FieldTypes introduced 2017-01-30.
        """
        self.assertEqual(len(FieldTypes), FieldTypes.F_BYTES32.value + 1)
        for ndx, _ in enumerate(FieldTypes):
            self.assertEqual(_.value, ndx)
            # round trip member to sym and back to member
            self.assertEqual(FieldTypes.from_sym(_.sym), _)

    def test_constants(self):
        """
        Verify that our constants are immutable and conversion between
        string and integer forms works as expected.
        """
        self.assertEqual(len(FieldTypes), 18)

        # pylint: disable=unsubscriptable-object
        self.assertEqual(FieldTypes.V_BOOL.value, 0)
        self.assertEqual(FieldTypes.V_BOOL.sym, 'vbool')

        self.assertEqual(FieldTypes.F_BYTES32.value, len(FieldTypes) - 1)
        self.assertEqual(FieldTypes.F_BYTES32.sym, 'fbytes32')

    def test_len_funcs(self):
        """
        Verify that varint length functions return correct values.

        Tests are performed using randomly selected field numbers
        (in the range 0 .. (2^16)-1) and integer values in the same
        range.
        """
        ndx = self.rng.next_int16()         # random field number
        value = self.rng.next_int16()        # random integer value

        # == varint types ===========================================
        # ERROR because field_hdr_len 2nd param should be PrimType
        # ********************************************************
        len_ = raw.field_hdr_len(ndx, FieldTypes.V_BOOL)
        self.assertEqual(len_ + 1, typed.vbool_len(True, ndx))
        self.assertEqual(len_ + 1, typed.vbool_len(False, ndx))

        len_ = raw.field_hdr_len(ndx, FieldTypes.V_ENUM)
        zzz = len_ + raw.length_as_varint(value)
        self.assertEqual(zzz, typed.venum_len(value, ndx))
        # self.assertEqual( x, typed.vEnumLen(-x, n) )

        value = self.rng.next_int32()
        self.assertTrue(value >= 0)

        len_ = raw.field_hdr_len(ndx, FieldTypes.V_UINT32)
        zzz = len_ + raw.length_as_varint(value)
        self.assertEqual(zzz, typed.vuint32_len(value, ndx))

        value = self.rng.next_int32()
        self.assertTrue(value >= 0)
        value = value - 0x80000000

        len_ = raw.field_hdr_len(ndx, FieldTypes.V_SINT32)
        ppp = typed.encode_sint32(value)
        zzz = len_ + raw.length_as_varint(ppp)
        self.assertEqual(zzz, typed.vsint32_len(value, ndx))

        value = self.rng.next_int64()
        self.assertTrue(value >= 0)

        len_ = raw.field_hdr_len(ndx, FieldTypes.V_UINT64)
        zzz = len_ + raw.length_as_varint(value)
        self.assertEqual(zzz, typed.vuint64_len(value, ndx))

        value = self.rng.next_int64()
        self.assertTrue(value >= 0)
        value = value - 0x8000000000000000

        len_ = raw.field_hdr_len(ndx, FieldTypes.V_SINT64)
        ppp = typed.encode_sint64(value)
        zzz = len_ + raw.length_as_varint(ppp)
        self.assertEqual(zzz, typed.vsint64_len(value, ndx))

        # == fixed length 4 byte ====================================
        value = self.rng.next_int64()        # value should be ignored

        self.assertTrue(value >= 0)
        value = value - 0x8000000000000000

        # x is a signed 64 bit value whose value should be irrelevant
        len_ = raw.field_hdr_len(ndx, FieldTypes.F_UINT32)
        self.assertEqual(len_ + 4, typed.fuint32_len(value, ndx))

        len_ = raw.field_hdr_len(ndx, FieldTypes.F_SINT32)
        self.assertEqual(len_ + 4, typed.fsint32_len(value, ndx))

        len_ = raw.field_hdr_len(ndx, FieldTypes.F_FLOAT)
        self.assertEqual(len_ + 4, typed.ffloat_len(value, ndx))

        # == fixed length 8 byte ====================================
        # n is that signed 64 bit value whose value should be irrelevant
        len_ = raw.field_hdr_len(ndx, FieldTypes.F_UINT64)
        self.assertEqual(len_ + 8, typed.fuint64_len(value, ndx))
        len_ = raw.field_hdr_len(ndx, FieldTypes.F_SINT64)
        self.assertEqual(len_ + 8, typed.fsint64_len(value, ndx))
        len_ = raw.field_hdr_len(ndx, FieldTypes.F_DOUBLE)
        self.assertEqual(len_ + 8, typed.fdouble_len(value, ndx))

        # == LEN PLUS types =========================================
        def do_len_plus_test(length, ndx):
            """
            Verify that fields of interesting lengths have expected
            raw encodings.
            """
            string = [0] * length
            k = len(string)
            len_ = raw.field_hdr_len(ndx, FieldTypes.L_BYTES)
            expected_len = len_ + raw.length_as_varint(k) + k
            self.assertEqual(expected_len, typed.lbytes_len(string, ndx))

        # -- lString ---------------------------------------
        string = self.rng.next_file_name(256)
        len_ = raw.field_hdr_len(ndx, FieldTypes.L_STRING)
        k = len(string)
        expected_len = len_ + raw.length_as_varint(k) + k
        self.assertEqual(expected_len, typed.l_string_len(string, ndx))

        # -- lBytes ----------------------------------------
        do_len_plus_test(0x7f, ndx)
        do_len_plus_test(0x80, ndx)
        do_len_plus_test(0x3fff, ndx)
        do_len_plus_test(0x4000, ndx)

        # -- lMsg ------------------------------------------
        # XXX STUB

        # -- fixed length byte arrays -------------------------------
        buf = [0] * 512       # length functions should ignore actual size

        len_ = raw.field_hdr_len(ndx, FieldTypes.F_BYTES16)
        self.assertEqual(len_ + 16, typed.fbytes16_len(buf, ndx))

        len_ = raw.field_hdr_len(ndx, FieldTypes.F_BYTES20)
        self.assertEqual(len_ + 20, typed.fbytes20_len(buf, ndx))

        len_ = raw.field_hdr_len(ndx, FieldTypes.F_BYTES32)
        self.assertEqual(len_ + 32, typed.fbytes32_len(buf, ndx))


if __name__ == '__main__':
    unittest.main()
