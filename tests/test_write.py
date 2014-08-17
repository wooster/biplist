from biplist import *
from biplist import PlistWriter
import datetime
import os
#from cStringIO import StringIO
import subprocess
import tempfile
from test_utils import *
import unittest
import six

class TestWritePlist(unittest.TestCase):
    def setUp(self):
        pass
    
    def roundTrip(self, root, xml=False, expected=None):
        # 'expected' is more fallout from the
        # don't-write-empty-unicode-strings issue.
        plist = writePlistToString(root, binary=(not xml))
        self.assertTrue(len(plist) > 0)
        readResult = readPlistFromString(plist)
        self.assertEqual(readResult, (expected if expected is not None else root))
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

    def testXMLPlistWithData(self):
        for binmode in (True, False):
            binplist = writePlistToString({'data': Data(six.b('\x01\xac\xf0\xff'))}, binary=binmode)
            plist = readPlistFromString(binplist)
            self.assertTrue(isinstance(plist['data'], (Data, six.binary_type)), \
                "unable to encode then decode Data into %s plist" % ("binary" if binmode else "XML"))

    def testConvertToXMLPlistWithData(self):
        binplist = writePlistToString({'data': Data(six.b('\x01\xac\xf0\xff'))})
        plist = readPlistFromString(binplist)
        xmlplist = writePlistToString(plist, binary=False)
        self.assertTrue(len(xmlplist) > 0, "unable to convert plist with Data from binary to XML")
    
    def testBoolRoot(self):
        self.roundTrip(True)
        self.roundTrip(False)
    
    def testDuplicate(self):
        l = ["foo" for i in range(0, 100)]
        self.roundTrip(l)
        
    def testListRoot(self):
        self.roundTrip([1, 2, 3])
    
    def testDictRoot(self):
        self.roundTrip({'a':1, 'B':'d'})
    
    def mixedNumericTypesHelper(self, cases):
        result = readPlistFromString(writePlistToString(cases))
        for i in range(0, len(cases)):
            self.assertTrue(cases[i] == result[i])
            self.assertEqual(type(cases[i]), type(result[i]), "Type mismatch on %d: %s != %s" % (i, repr(cases[i]), repr(result[i])))
    
    def reprChecker(self, case):
        result = readPlistFromString(writePlistToString(case))
        self.assertEqual(repr(case), repr(result))
    
    def testBoolsAndIntegersMixed(self):
        self.mixedNumericTypesHelper([0, 1, True, False, None])
        self.mixedNumericTypesHelper([False, True, 0, 1, None])
        self.reprChecker({'1':[True, False, 1, 0], '0':[1, 2, 0, {'2':[1, 0, False]}]})
        self.reprChecker([1, 1, 1, 1, 1, True, True, True, True])
    
    def testFloatsAndIntegersMixed(self):
        self.mixedNumericTypesHelper([0, 1, 1.0, 0.0, None])
        self.mixedNumericTypesHelper([0.0, 1.0, 0, 1, None])
        self.reprChecker({'1':[1.0, 0.0, 1, 0], '0':[1, 2, 0, {'2':[1, 0, 0.0]}]})
        self.reprChecker([1, 1, 1, 1, 1, 1.0, 1.0, 1.0, 1.0])
    
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
        self.assertEqual(readResult['aTuple'], [1, 2.0, 'a'])
        self.assertEqual(readResult['dupTuple'], ['a', 'a', 'a', 'b', 'b'])
    
    def testComplicated(self):
        root = {'preference':[1, 2, {'hi there':['a', 1, 2, {'yarrrr':123}]}]}
        self.lintPlist(writePlistToString(root))
        self.roundTrip(root)
    
    def testString(self):
        self.roundTrip(six.b('0'))
        self.roundTrip(six.b(''))
        self.roundTrip({six.b('a'):six.b('')})
    
    def testLargeDict(self):
        d = {}
        for i in range(0, 1000):
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
            with open(path, 'rb') as f:
                self.lintPlist(f.read())
    
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
            self.roundTrip({Data(six.b("hello world")):1})
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
        edges = [-pow(2, 7), pow(2, 7) - 1, 
                 -pow(2, 15), pow(2, 15) - 1, 
                 -pow(2, 31), pow(2, 31) - 1, 
                 -pow(2, 63), pow(2, 64) - 1]
        self.roundTrip(edges)
        
        io = six.BytesIO()
        writer = PlistWriter(io)
        bytes = [(1, [pow(2, 7) - 1]),
                 (2, [pow(2, 15) - 1]),
                 (4, [pow(2, 31) - 1]),
                 (8, [-pow(2, 7), -pow(2, 15), -pow(2, 31), -pow(2, 63), pow(2, 63) - 1]),
                 (16, [pow(2, 64) - 1])
            ]
        for bytelen, tests in bytes:
            for test in tests:
                got = writer.intSize(test)
                self.assertEqual(bytelen, got, "Byte size is wrong. Expected %d, got %d" % (bytelen, got))
        
        bytes_lists = [list(x) for x in bytes]
        self.roundTrip(bytes_lists)
        
        try:
            self.roundTrip([0x10000000000000000, pow(2, 64)])
            self.fail("2^64 should be too large for Core Foundation to handle.")
        except InvalidPlistException as e:
            pass
    
    def testWriteData(self):
        self.roundTrip(Data(six.b("woohoo")))
        
    def testUnicode(self):
        unicodeRoot = six.u("Mirror's Edge\u2122 for iPad")
        writePlist(unicodeRoot, "/tmp/odd.plist")
        self.roundTrip(unicodeRoot)
        unicodeStrings = [six.u("Mirror's Edge\u2122 for iPad"), six.u('Weightbot \u2014 Track your Weight in Style')]
        self.roundTrip(unicodeStrings)
        self.roundTrip({six.u(""):six.u("")}, expected={six.b(''):six.b('')})
        self.roundTrip(six.u(""), expected=six.b(''))
        
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
