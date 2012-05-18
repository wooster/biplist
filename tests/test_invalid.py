from biplist import *
import os
from test_utils import *
import unittest

class TestInvalidPlistFile(unittest.TestCase):
    def setUp(self):
        pass
    def testEmptyFile(self):
        try:
            readPlist(data_path('empty_file.plist'))
            self.fail("Should not successfully read empty plist.")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testTooShort(self):
        try:
            readPlistFromString(six.b("bplist0"))
            self.fail("Should not successfully read plist which is too short.")
        except InvalidPlistException as e:
            pass
    
    def testInvalid(self):
        try:
            readPlistFromString(six.b("bplist0-------------------------------------"))
            self.fail("Should not successfully read invalid plist.")
        except InvalidPlistException as e:
            pass
        
if __name__ == '__main__':
    unittest.main()
