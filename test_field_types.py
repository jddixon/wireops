#!/usr/bin/env python3
# testFieldTypes.py

""" Exercise the FieldTypes class. """

import time
import unittest

from wireops.field_types import FieldTypes, FieldStr

import wireops.raw as R
import wireops.typed as T
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

    def test_constants(self):
        """
        Verify that our constants are immutable and conversion between
        string and integer forms works as expected.
        """
        self.assertEqual(0, FieldTypes.V_BOOL)
        self.assertEqual(FieldStr.as_str(FieldTypes.V_BOOL), 'vbool')

        self.assertEqual(19, FieldTypes.F_BYTES32)
        self.assertEqual(FieldStr.as_str(FieldTypes.F_BYTES32), 'fbytes32')
        try:
            FieldTypes.V_BOOL = 47
        except AttributeError:
            # 'success: caught attempt to reassign constant'
            pass

        for type_ in range(FieldTypes.MAX_NDX + 1):
            type_name = FieldStr.as_str(type_)
            self.assertEqual(FieldStr.ndx(name=type_name), type_)

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
        len_ = R.field_hdr_len(ndx, FieldTypes.V_BOOL)
        self.assertEqual(len_ + 1, T.vbool_len(True, ndx))
        self.assertEqual(len_ + 1, T.vbool_len(False, ndx))

        len_ = R.field_hdr_len(ndx, FieldTypes.V_ENUM)
        zzz = len_ + R.length_as_varint(value)
        self.assertEqual(zzz, T.venum_len(value, ndx))
        # self.assertEqual( x, T.vEnumLen(-x, n) )

        value = self.rng.next_int32()
        self.assertTrue(value >= 0)

        len_ = R.field_hdr_len(ndx, FieldTypes.V_UINT32)
        zzz = len_ + R.length_as_varint(value)
        self.assertEqual(zzz, T.vuint32_len(value, ndx))

        value = self.rng.next_int32()
        self.assertTrue(value >= 0)
        value = value - 0x80000000

        len_ = R.field_hdr_len(ndx, FieldTypes.V_SINT32)
        ppp = T.encode_sint32(value)
        zzz = len_ + R.length_as_varint(ppp)
        self.assertEqual(zzz, T.vsint32_len(value, ndx))

        value = self.rng.next_int64()
        self.assertTrue(value >= 0)

        len_ = R.field_hdr_len(ndx, FieldTypes.V_UINT64)
        zzz = len_ + R.length_as_varint(value)
        self.assertEqual(zzz, T.vuint64_len(value, ndx))

        value = self.rng.next_int64()
        self.assertTrue(value >= 0)
        value = value - 0x8000000000000000

        len_ = R.field_hdr_len(ndx, FieldTypes.V_SINT64)
        ppp = T.encode_sint64(value)
        zzz = len_ + R.length_as_varint(ppp)
        self.assertEqual(zzz, T.vsint64_len(value, ndx))

        # == fixed length 4 byte ====================================
        value = self.rng.next_int64()        # value should be ignored

        self.assertTrue(value >= 0)
        value = value - 0x8000000000000000

        # x is a signed 64 bit value whose value should be irrelevant
        len_ = R.field_hdr_len(ndx, FieldTypes.F_UINT32)
        self.assertEqual(len_ + 4, T.fuint32_len(value, ndx))

        len_ = R.field_hdr_len(ndx, FieldTypes.F_SINT32)
        self.assertEqual(len_ + 4, T.fsint32_len(value, ndx))

        len_ = R.field_hdr_len(ndx, FieldTypes.F_FLOAT)
        self.assertEqual(len_ + 4, T.ffloat_len(value, ndx))

        # == fixed length 8 byte ====================================
        # n is that signed 64 bit value whose value should be irrelevant
        len_ = R.field_hdr_len(ndx, FieldTypes.F_UINT64)
        self.assertEqual(len_ + 8, T.fuint64_len(value, ndx))
        len_ = R.field_hdr_len(ndx, FieldTypes.F_SINT64)
        self.assertEqual(len_ + 8, T.fsint64_len(value, ndx))
        len_ = R.field_hdr_len(ndx, FieldTypes.F_DOUBLE)
        self.assertEqual(len_ + 8, T.fdouble_len(value, ndx))

        # == LEN PLUS types =========================================
        def do_len_plus_test(length, ndx):
            """
            Verify that fields of interesting lengths have expected
            raw encodings.
            """
            string = [0] * length
            k = len(string)
            len_ = R.field_hdr_len(ndx, FieldTypes.L_BYTES)
            expected_len = len_ + R.length_as_varint(k) + k
            self.assertEqual(expected_len, T.lbytes_len(string, ndx))

        # -- lString ---------------------------------------
        string = self.rng.next_file_name(256)
        len_ = R.field_hdr_len(ndx, FieldTypes.L_STRING)
        k = len(string)
        expected_len = len_ + R.length_as_varint(k) + k
        self.assertEqual(expected_len, T.l_string_len(string, ndx))

        # -- lBytes ----------------------------------------
        do_len_plus_test(0x7f, ndx)
        do_len_plus_test(0x80, ndx)
        do_len_plus_test(0x3fff, ndx)
        do_len_plus_test(0x4000, ndx)

        # -- lMsg ------------------------------------------
        # XXX STUB

        # -- fixed length byte arrays -------------------------------
        buf = [0] * 512       # length functions should ignore actual size

        len_ = R.field_hdr_len(ndx, FieldTypes.F_BYTES16)
        self.assertEqual(len_ + 16, T.fbytes16_len(buf, ndx))

        len_ = R.field_hdr_len(ndx, FieldTypes.F_BYTES20)
        self.assertEqual(len_ + 20, T.fbytes20_len(buf, ndx))

        len_ = R.field_hdr_len(ndx, FieldTypes.F_BYTES32)
        self.assertEqual(len_ + 32, T.fbytes32_len(buf, ndx))

if __name__ == '__main__':
    unittest.main()
