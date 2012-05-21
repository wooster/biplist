from biplist import *
import datetime
import os
from test_utils import *
import unittest

class TestValidPlistFile(unittest.TestCase):
    def setUp(self):
        pass
    
    def validateSimpleBinaryRoot(self, root):
        self.assertTrue(type(root) == dict, "Root should be dictionary.")
        self.assertTrue(type(root['dateItem']) == datetime.datetime, "date should be datetime")
        self.assertEquals(root['dateItem'], datetime.datetime(2010, 8, 19, 22, 27, 30, 385449), "dates not equal" )
        self.assertEquals(root['numberItem'], -10000000000000000L, "number not of expected value")
        self.assertEquals(root['unicodeItem'], u'abc\u212cdef\u2133')
        self.assertEquals(root['stringItem'], 'Hi there')
        self.assertEquals(root['realItem'], 0.47)
        self.assertEquals(root['boolItem'], True)
        self.assertEquals(root['arrayItem'], ['item0'])
        
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
        self.assertEquals(result, u"Mirror's Edge\u2122 for iPad")
    
    def testEmptyUnicodeRoot(self):
        result = readPlist(data_path('unicode_empty.plist'))
        self.assertEquals(result, u"")
    
    def testSmallReal(self):
        result = readPlist(data_path('small_real.plist'))
        self.assertEquals(result, {'4 byte real':0.5})
    
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
        self.assertEquals(result, {'$version': 100000, 
            '$objects': 
                ['$null', 
                 {'$class': Uid(3), 'somekey': Uid(2)}, 
                 'object value as string', 
                 {'$classes': ['Archived', 'NSObject'], '$classname': 'Archived'}
                 ], 
            '$top': {'root': Uid(1)}, '$archiver': 'NSKeyedArchiver'})
        self.assertEquals("Uid(1)", repr(Uid(1)))
    
if __name__ == '__main__':
    unittest.main()
