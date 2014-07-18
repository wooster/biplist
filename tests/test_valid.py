from biplist import *
import datetime
import os
from test_utils import *
import unittest
import six

class TestValidPlistFile(unittest.TestCase):
    def setUp(self):
        pass
    
    def validateSimpleBinaryRoot(self, root):
        self.assertTrue(type(root) == dict, "Root should be dictionary.")
        self.assertTrue(type(root[six.b('dateItem')]) == datetime.datetime, "date should be datetime")
        us = root[six.b('dateItem')].microsecond
        if us == 385448:
            # Python 3 doesn't round microseconds to the nearest value.
            self.assertEqual(root[six.b('dateItem')], datetime.datetime(2010, 8, 19, 22, 27, 30, 385448), "dates not equal" )
        else:
            self.assertEqual(root[six.b('dateItem')], datetime.datetime(2010, 8, 19, 22, 27, 30, 385449), "dates not equal" )
        self.assertEqual(root[six.b('numberItem')], -10000000000000000, "number not of expected value")
        self.assertEqual(root[six.b('unicodeItem')], six.u('abc\u212cdef\u2133'))
        self.assertEqual(root[six.b('stringItem')], six.b('Hi there'))
        self.assertEqual(root[six.b('realItem')], 0.47)
        self.assertEqual(root[six.b('boolItem')], True)
        self.assertEqual(root[six.b('arrayItem')], [six.b('item0')])
        
    def testFileRead(self):
        try:
            result = readPlist(data_path('simple_binary.plist'))
            self.validateSimpleBinaryRoot(result)
        except NotBinaryPlistException as e:
            self.fail("NotBinaryPlistException: %s" % e)
        except InvalidPlistException as e:
            self.fail("InvalidPlistException: %s" % e)
    
    def testUnicodeRoot(self):
        result = readPlist(data_path('unicode_root.plist'))
        self.assertEqual(result, six.u("Mirror's Edge\u2122 for iPad"))
    
    def testEmptyUnicodeRoot(self):
        # Porting note: this test was tricky; it was only passing in
        # Python 2 because the empty byte-string returned by
        # readPlist() is considered equal to the empty unicode-string
        # in the assertion.  Confusingly enough, given the name of the
        # test, the value in unicode_empty.plist has the format byte
        # 0b0101 (ASCII string), so the value being asserted against
        # appears to be what is wrong.
        result = readPlist(data_path('unicode_empty.plist'))
        self.assertEqual(result, six.b(""))
    
    def testSmallReal(self):
        result = readPlist(data_path('small_real.plist'))
        self.assertEqual(result, {six.b('4 byte real'):0.5})
    
    def testLargeIntegers(self):
        result = readPlist(data_path('large_int_limits.plist'))
        self.assertEqual(result[six.b('Max 8 Byte Unsigned Integer')], 18446744073709551615)
        self.assertEqual(result[six.b('Min 8 Byte Signed Integer')], -9223372036854775808)
        self.assertEqual(result[six.b('Max 8 Byte Signed Integer')], 9223372036854775807)

    def testKeyedArchiverPlist(self):
        """
        Archive is created with class like this:
        @implementation Archived
        ...
        - (void)encodeWithCoder:(NSCoder *)coder {
            [coder encodeObject:@"object value as string" forKey:@"somekey"];
        }
        @end
        
        Archived *test = [[Archived alloc] init];
        NSData *data = [NSKeyedArchiver archivedDataWithRootObject:test]
        ...
        """
        result = readPlist(data_path('nskeyedarchiver_example.plist'))
        self.assertEqual(result, {six.b('$version'): 100000, 
            six.b('$objects'): 
                [six.b('$null'),
                 {six.b('$class'): Uid(3), six.b('somekey'): Uid(2)}, 
                 six.b('object value as string'),
                 {six.b('$classes'): [six.b('Archived'), six.b('NSObject')], six.b('$classname'): six.b('Archived')}
                 ], 
            six.b('$top'): {six.b('root'): Uid(1)}, six.b('$archiver'): six.b('NSKeyedArchiver')})
        self.assertEqual("Uid(1)", repr(Uid(1)))
    
if __name__ == '__main__':
    unittest.main()
