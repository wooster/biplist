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
            readPlist(fuzz_data_path('listIndexOutOfRange.plist'))
            self.fail("list index out of range, should fail")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testInvalidMarkerByteUnpack(self):
        try:
            readPlist(fuzz_data_path('noMarkerByte.plist'))
            self.fail("No marker byte at object offset")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testInvalidObjectOffset(self):
        try:
            readPlist(fuzz_data_path('invalidObjectOffset.plist'))
            self.fail("Invalid object offset in offsets table")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testRecursiveObjectOffset(self):
        try:
            readPlist(fuzz_data_path('recursiveObjectOffset.plist'))
            self.fail("Recursive object found")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testExcessivelyLongAsciiString(self):
        try:
            readPlist(fuzz_data_path('asciiStringTooLong.plist'))
            self.fail("ASCII string extends into trailer")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testNegativelyLongAsciiString(self):
        try:
            readPlist(fuzz_data_path('asciiStringNegativeLength.plist'))
            self.fail("ASCII string length less than zero")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testInvalidOffsetEnding(self):
        # The end of the offset is past the end of the offset table.
        try:
            readPlist(fuzz_data_path('invalidOffsetEnding.plist'))
            self.fail("End of offset after end of offset table")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testInvalidDictionaryObjectCount(self):
        try:
            readPlist(fuzz_data_path('dictionaryInvalidCount.plist'))
            self.fail("Dictionary object count is not of integer type")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testInvalidArrayObjectCount(self):
        try:
            readPlist(fuzz_data_path('arrayInvalidCount.plist'))
            self.fail("Array object count is not of integer type")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testInvalidRealLength(self):
        try:
            readPlist(fuzz_data_path('realInvalidLength.plist'))
            self.fail("Real length is not of integer type")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testNaNDateSeconds(self):
        try:
            readPlist(fuzz_data_path('dateSecondsIsNaN.plist'))
            self.fail("Date seconds is NaN")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testIntegerWithZeroByteLength(self):
        try:
            readPlist(fuzz_data_path('integerZeroByteLength.plist'))
            self.fail("Integer has byte size of 0.")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass

