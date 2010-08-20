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
        
    def test_file_read(self):
        try:
            result = readPlist(fixture_path('simple_binary.plist'))
            self.validateSimpleBinaryRoot(result)
            self.fail('remove me')
        except NotBinaryPlistException, e:
            self.fail("NotBinaryPlistException: %s" % e)
        except InvalidPlistException, e:
            self.fail("InvalidPlistException: %s" % e)
        
if __name__ == '__main__':
    unittest.main()
