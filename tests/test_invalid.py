#!/usr/bin/env python

import os, sys, unittest

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from biplist import *

dataPath = os.path.join(os.path.dirname(__file__), 'data')

class TestInvalidPlistFile(unittest.TestCase):
    def setUp(self):
        pass
    def testEmptyFile(self):
        try:
            readPlist(os.path.join(dataPath, 'empty_file.plist'))
            self.fail("Should not successfully read empty plist.")
        except NotBinaryPlistException as e:
            pass
        except InvalidPlistException as e:
            pass
    
    def testTooShort(self):
        try:
            readPlistFromString(b"bplist0")
            self.fail("Should not successfully read plist which is too short.")
        except InvalidPlistException as e:
            pass
    
    def testInvalid(self):
        try:
            readPlistFromString(b"bplist0-------------------------------------")
            self.fail("Should not successfully read invalid plist.")
        except InvalidPlistException as e:
            pass
        
if __name__ == '__main__':
    unittest.main()
