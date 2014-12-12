#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime, os, sys, unittest

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from biplist import *

dataPath = os.path.join(os.path.dirname(__file__), 'data')

try:
    unicode
    unicodeStr = lambda x: x.decode('utf-8')
except NameError:
    unicode = str
    unicodeStr = lambda x: x

class TestValidPlistFile(unittest.TestCase):
    
    def validateSimpleBinaryRoot(self, root):
        self.assertTrue(type(root) == dict, "Root should be dictionary.")
        self.assertTrue(type(root['dateItem']) == datetime.datetime, "date should be datetime")
        us = root['dateItem'].microsecond
        if us == 385448:
            # Python 3 doesn't round microseconds to the nearest value.
            self.assertEqual(root['dateItem'], datetime.datetime(2010, 8, 19, 22, 27, 30, 385448), "dates not equal" )
        else:
            self.assertEqual(root['dateItem'], datetime.datetime(2010, 8, 19, 22, 27, 30, 385449), "dates not equal" )
        self.assertEqual(root['numberItem'], -10000000000000000, "number not of expected value")
        self.assertEqual(root['unicodeItem'], unicodeStr('abcℬdefℳ'))
        self.assertEqual(root['stringItem'], 'Hi there')
        self.assertEqual(root['realItem'], 0.47)
        self.assertEqual(root['boolItem'], True)
        self.assertEqual(root['arrayItem'], ['item0'])
        
    def testFileRead(self):
        try:
            result = readPlist(os.path.join(dataPath, 'simple_binary.plist'))
            self.validateSimpleBinaryRoot(result)
        except NotBinaryPlistException as e:
            self.fail("NotBinaryPlistException: %s" % e)
        except InvalidPlistException as e:
            self.fail("InvalidPlistException: %s" % e)
    
    def testUnicodeRoot(self):
        result = readPlist(os.path.join(dataPath, 'unicode_root.plist'))
        self.assertEqual(result, unicodeStr("Mirror's Edge™ for iPad"))
    
    def testEmptyUnicodeRoot(self):
        # Porting note: this test was tricky; it was only passing in
        # Python 2 because the empty byte-string returned by
        # readPlist() is considered equal to the empty unicode-string
        # in the assertion.  Confusingly enough, given the name of the
        # test, the value in unicode_empty.plist has the format byte
        # 0b0101 (ASCII string), so the value being asserted against
        # appears to be what is wrong.
        result = readPlist(os.path.join(dataPath, 'unicode_empty.plist'))
        self.assertEqual(result, '')
    
    def testSmallReal(self):
        result = readPlist(os.path.join(dataPath, 'small_real.plist'))
        self.assertEqual(result, {'4 byte real':0.5})
    
    def testLargeIntegers(self):
        result = readPlist(os.path.join(dataPath, 'large_int_limits.plist'))
        self.assertEqual(result['Max 8 Byte Unsigned Integer'], 18446744073709551615)
        self.assertEqual(result['Min 8 Byte Signed Integer'], -9223372036854775808)
        self.assertEqual(result['Max 8 Byte Signed Integer'], 9223372036854775807)
    
    def testLargeDates(self):
        result = readPlist(os.path.join(dataPath, "BFPersistentEventInfo.plist"))
        self.assertEqual(result['lastShownRatePromptDate'], datetime.datetime(1, 12, 30, 0, 0, 0))

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
        result = readPlist(os.path.join(dataPath, 'nskeyedarchiver_example.plist'))
        self.assertEqual(result, {
        	'$version': 100000, 
            '$objects':
                [
                	'$null',
                 	{'$class':Uid(3), 'somekey':Uid(2)}, 
                 	'object value as string',
                 	{'$classes':['Archived', 'NSObject'], '$classname':'Archived'}
                ],
			'$top': {'root':Uid(1)},
			'$archiver':'NSKeyedArchiver'
        })
        self.assertEqual("Uid(1)", repr(Uid(1)))
    
if __name__ == '__main__':
    unittest.main()
