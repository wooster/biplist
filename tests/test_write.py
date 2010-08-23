from biplist import *
import datetime
import os
import subprocess
import tempfile
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
        self.lintPlist(plist)
    
    def lintPlist(self, plistString):
        if os.path.exists('/usr/bin/plutil'):
            f = tempfile.NamedTemporaryFile()
            f.write(plistString)
            f.flush()
            name = f.name
            (status, output) = run_command(['/usr/bin/plutil', '-lint', name])
            if status != 0:
                self.fail("plutil verification failed (status %d): %s" % (status, output))
    
    def testBoolRoot(self):
        self.roundTrip(True)
        
    def testListRoot(self):
        self.roundTrip([1, 2, 3])
    
    def testDictRoot(self):
        self.roundTrip({'a':1, 'B':'d'})
    
    def testSetRoot(self):
        self.roundTrip(set((1, 2, 3)))
    
    def testFloat(self):
        self.roundTrip({'aFloat':1.23})
    
    def testTuple(self):
        result = writePlistToString({'aTuple':(1, 2.0, 'a')})
        self.assertTrue(len(result) > 0)
        readResult = readPlistFromString(result)
        self.assertEquals(readResult['aTuple'], [1, 2.0, 'a'])
    
    def testComplicated(self):
        root = {'preference':[1, 2, {'hi there':['a', 1, 2, {'yarrrr':123}]}]}
        self.lintPlist(writePlistToString(root))
        self.roundTrip(root)
    
    def testString(self):
        self.roundTrip('0')
    
    def testLargeDict(self):
        d = {}
        for i in xrange(0, 1000):
            d['%d' % i] = '%d' % i
        self.roundTrip(d)
    
    def testUniques(self):
        root = {'hi':'there', 'halloo':'there'}
        self.roundTrip(root)
    
    def testWriteToFile(self):
        path = '/var/tmp/test.plist'
        writePlist([1, 2, 3], path)
        self.assertTrue(os.path.exists(path))
        self.lintPlist(open(path).read())
    
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
        try:
            self.roundTrip({Data("hello world"):1})
            self.fail("Data is not a valid key in Cocoa.")
        except InvalidPlistException, e:
            pass
    
    def testWriteData(self):
        self.roundTrip(Data("woohoo"))

if __name__ == '__main__':
    unittest.main()
