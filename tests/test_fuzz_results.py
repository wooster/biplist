# -*- coding: utf-8 -*-

from biplist import *
import os
from test_utils import *
import unittest

class TestFuzzResults(unittest.TestCase):
    def setUp(self):
        pass
    
    def testCurrentOffsetOutOfRange(self):
        try:
            readPlist(fuzz_data_path('id_000000,sig_30,src_000001,op_flip1,pos_8'))
            self.fail("list index out of range, should fail")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testInvalidMarkerByteUnpack(self):
        try:
            readPlist(fuzz_data_path('id_000001,sig_30,src_000001,op_flip1,pos_9'))
            self.fail("No marker byte at object offset")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testInvalidObjectOffset(self):
        try:
            readPlist(fuzz_data_path('id_000003,sig_30,src_000001,op_flip1,pos_25'))
            self.fail("Invalid object offset in offsets table")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testRecursiveObjectOffset(self):
        try:
            readPlist(fuzz_data_path('id_000012,sig_30,src_000005,op_flip1,pos_9'))
            self.fail("Recursive object found")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testExcessivelyLongAsciiString(self):
        try:
            readPlist(fuzz_data_path('id_000016,sig_30,src_000005,op_flip1,pos_91'))
            self.fail("ASCII string extends into trailer")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testNegativelyLongAsciiString(self):
        try:
            readPlist(fuzz_data_path('id_000000,sig_30,src_000005,op_flip4,pos_91'))
            self.fail("ASCII string length less than zero")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testInvalidOffsetEnding(self):
        # The end of the offset is past the end of the offset table.
        try:
            readPlist(fuzz_data_path('id_000033,sig_30,src_000005,op_arith8,pos_225,val_+3'))
            self.fail("End of offset after end of offset table")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testInvalidDictionaryObjectCount(self):
        try:
            readPlist(fuzz_data_path('id_000049,sig_30,src_000006,op_flip4,pos_8'))
            self.fail("Dictionary object count is not of integer type")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testInvalidArrayObjectCount(self):
        try:
            readPlist(fuzz_data_path('id_000068,sig_30,src_000089,op_int8,pos_189,val_-128'))
            self.fail("Array object count is not of integer type")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testInvalidRealLength(self):
        try:
            readPlist(fuzz_data_path('id_000077,sig_30,src_000103,op_arith8,pos_92,val_+12'))
            self.fail("Real length is not of integer type")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testNaNDateSeconds(self):
        try:
            readPlist(fuzz_data_path('id_000050,sig_30,src_000006,op_int16,pos_106,val_-1'))
            self.fail("Date seconds is NaN")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testIntegerWithZeroByteLength(self):
        try:
            readPlist(fuzz_data_path('id_000000,src_000005,op_arith8,pos_149,val_+13'))
            self.fail("Integer has byte size of 0.")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass

