from biplist import *
import os
from test_utils import *
import unittest

class TestValidPlistFile(unittest.TestCase):
    def setUp(self):
        pass
    def test_file_read(self):
        try:
            result = readPlist(fixture_path('simple_binary.plist'))
            self.assertTrue(type(result) == dict, "Result should be dictionary.")
        except NotBinaryPlistException, e:
            self.fail("NotBinaryPlistException: %s" % e)
        except InvalidPlistException, e:
            self.fail("InvalidPlistException: %s" % e)
        
if __name__ == '__main__':
    unittest.main()
