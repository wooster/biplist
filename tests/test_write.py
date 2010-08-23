from biplist import *
import datetime
import os
from test_utils import *
import unittest

class TestWritePlist(unittest.TestCase):
    def setUp(self):
        pass
    
    def roundTrip(self, root):
        plist = writePlistToString(root)
        self.assertTrue(len(plist) > 0)
        readResult = readPlistFromString(plist)
        self.assertEquals(readResult, root)
    
    def testBoolRoot(self):
        self.roundTrip(True)
        
    def testListRoot(self):
        self.roundTrip([1, 2, 3])
    
    def testDictRoot(self):
        self.roundTrip({'a':1, 'B':'d'})
    
    def testSetRoot(self):
        self.roundTrip(set((1, 2, 3)))
    
    def testComplicated(self):
        root = {'preference':[1, 2, {'hi there':['a', 1, 2, {'yarrrr':123}]}]}
        #!! Replace with plutil verification
        writePlist(root, '/var/tmp/d3.plist')
        self.roundTrip(root)
    
    def testString(self):
        self.roundTrip('0')
    
    def testLargeDict(self):
        d = {}
        for i in xrange(0, 1000):
            d['%d' % i] = '%d' % i
        #!! Replace with plutil verification
        writePlist(d, '/var/tmp/d.plist')
        self.roundTrip(d)
    
    def testUniques(self):
        root = {'hi':'there', 'halloo':'there'}
        self.roundTrip(root)
    
    def testWriteToFile(self):
        writePlist([1, 2, 3], '/var/tmp/test.plist')
        self.assertTrue(os.path.exists('/var/tmp/test.plist'))
    
    def testNone(self):
        self.roundTrip(None)
        self.roundTrip({'1':None})
        self.roundTrip([None, None, None])
    
    def testBadKeys(self):
        try:
            self.roundTrip({None:1})
            self.fail("None is not a valid key in Cocoa.")
        except InvalidPlistException, e:
            pass

if __name__ == '__main__':
    unittest.main()
