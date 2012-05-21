from biplist import *
from biplist import PlistWriter
import datetime
import os
from cStringIO import StringIO
import subprocess
import tempfile
from test_utils import *
import unittest

class TestWritePlist(unittest.TestCase):
    def setUp(self):
        pass
    
    def roundTrip(self, root, xml=False):
        plist = writePlistToString(root, binary=(not xml))
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
    
    def testXMLPlist(self):
        self.roundTrip({'hello':'world'}, xml=True)
    
    def testBoolRoot(self):
        self.roundTrip(True)
        self.roundTrip(False)
    
    def testDuplicate(self):
        l = ["foo" for i in xrange(0, 100)]
        self.roundTrip(l)
        
    def testListRoot(self):
        self.roundTrip([1, 2, 3])
    
    def testDictRoot(self):
        self.roundTrip({'a':1, 'B':'d'})
    
    def boolsAndIntegersHelper(self, cases):
        result = readPlistFromString(writePlistToString(cases))
        for i in range(0, len(cases)):
            self.assertTrue(cases[i] == result[i])
            self.assertEquals(type(cases[i]), type(result[i]), "Type mismatch on %d: %s != %s" % (i, repr(cases[i]), repr(result[i])))
    
    def reprChecker(self, case):
        result = readPlistFromString(writePlistToString(case))
        self.assertEquals(repr(case), repr(result))
    
    def testBoolsAndIntegersMixed(self):
        self.boolsAndIntegersHelper([0, 1, True, False, None])
        self.boolsAndIntegersHelper([False, True, 0, 1, None])
        self.reprChecker({'1':[True, False, 1, 0], '0':[1, 2, 0, {'2':[1, 0, False]}]})
        self.reprChecker([1, 1, 1, 1, 1, True, True, True, True])
    
    def testSetRoot(self):
        self.roundTrip(set((1, 2, 3)))
    
    def testDatetime(self):
        now = datetime.datetime.utcnow()
        now = now.replace(microsecond=0)
        self.roundTrip([now])
    
    def testFloat(self):
        self.roundTrip({'aFloat':1.23})
    
    def testTuple(self):
        result = writePlistToString({'aTuple':(1, 2.0, 'a'), 'dupTuple':('a', 'a', 'a', 'b', 'b')})
        self.assertTrue(len(result) > 0)
        readResult = readPlistFromString(result)
        self.assertEquals(readResult['aTuple'], [1, 2.0, 'a'])
        self.assertEquals(readResult['dupTuple'], ['a', 'a', 'a', 'b', 'b'])
    
    def testComplicated(self):
        root = {'preference':[1, 2, {'hi there':['a', 1, 2, {'yarrrr':123}]}]}
        self.lintPlist(writePlistToString(root))
        self.roundTrip(root)
    
    def testString(self):
        self.roundTrip('0')
        self.roundTrip('')
        self.roundTrip({'a':''})
    
    def testLargeDict(self):
        d = {}
        for i in xrange(0, 1000):
            d['%d' % i] = '%d' % i
        self.roundTrip(d)
        
    def testBools(self):
        self.roundTrip([True, False])
    
    def testUniques(self):
        root = {'hi':'there', 'halloo':'there'}
        self.roundTrip(root)
    
    def testWriteToFile(self):
        for is_binary in [True, False]:
            path = '/var/tmp/test.plist'
            writePlist([1, 2, 3], path, binary=is_binary)
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
        except InvalidPlistException as e:
            pass
        try:
            self.roundTrip({Data("hello world"):1})
            self.fail("Data is not a valid key in Cocoa.")
        except InvalidPlistException as e:
            pass
        try:
            self.roundTrip({1:1})
            self.fail("Number is not a valid key in Cocoa.")
        except InvalidPlistException as e:
            pass
    
    def testIntBoundaries(self):
        edges = [0xff, 0xffff, 0xffffffff]
        for edge in edges:
            cases = [edge, edge-1, edge+1, edge-2, edge+2, edge*2, edge/2]
            self.roundTrip(cases)
        edges = [-pow(2, 7), pow(2, 7) - 1, -pow(2, 15), pow(2, 15) - 1, -pow(2, 31), pow(2, 31) - 1]
        self.roundTrip(edges)
        
        io = StringIO()
        writer = PlistWriter(io)
        bytes = [(1, [pow(2, 7) - 1]),
                 (2, [pow(2, 15) - 1]),
                 (4, [pow(2, 31) - 1]),
                 (8, [-pow(2, 7), -pow(2, 15), -pow(2, 31), -pow(2, 63), pow(2, 63) - 1])
            ]
        for bytelen, tests in bytes:
            for test in tests:
                got = writer.intSize(test)
                self.assertEquals(bytelen, got, "Byte size is wrong. Expected %d, got %d" % (bytelen, got))
        
        bytes_lists = [list(x) for x in bytes]
        self.roundTrip(bytes_lists)
        
        try:
            self.roundTrip([0x8000000000000000, pow(2, 63)])
            self.fail("2^63 should be too large for Core Foundation to handle.")
        except InvalidPlistException as e:
            pass
    
    def testWriteData(self):
        self.roundTrip(Data("woohoo"))
        
    def testUnicode(self):
        unicodeRoot = u"Mirror's Edge\u2122 for iPad"
        writePlist(unicodeRoot, "/tmp/odd.plist")
        self.roundTrip(unicodeRoot)
        unicodeStrings = [u"Mirror's Edge\u2122 for iPad", u'Weightbot \u2014 Track your Weight in Style']
        self.roundTrip(unicodeStrings)
        self.roundTrip({u"":u""})
        self.roundTrip(u"")
        
    def testUidWrite(self):
        self.roundTrip({'$version': 100000, 
            '$objects': 
                ['$null', 
                 {'$class': Uid(3), 'somekey': Uid(2)}, 
                 'object value as string', 
                 {'$classes': ['Archived', 'NSObject'], '$classname': 'Archived'}
                 ], 
            '$top': {'root': Uid(1)}, '$archiver': 'NSKeyedArchiver'})

if __name__ == '__main__':
    unittest.main()
