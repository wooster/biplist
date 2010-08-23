from collections import namedtuple
from cStringIO import StringIO
import datetime
import math
import plistlib
from struct import pack, unpack
import time

__all__ = [
    'Uid', 'Data', 'readPlist', 'writePlist', 'readPlistFromString',
    'writePlistToString', 'InvalidPlistException', 'NotBinaryPlistException'
]

apple_reference_date_offset = 978307200

class Uid(int):
    """Wrapper around integers for representing UID values."""
    pass

class Data(str):
    """Wrapper around str types for representing Data values."""
    pass
    

class InvalidPlistException(Exception):
    """Raised when the plist is incorrectly formatted."""
    pass

class NotBinaryPlistException(Exception):
    """Raised when a binary plist was expected but not encountered."""
    pass

def readPlist(pathOrFile):
    """Raises NotBinaryPlistException, InvalidPlistException"""
    didOpen = False
    result = None
    if isinstance(pathOrFile, (str, unicode)):
        pathOrFile = open(pathOrFile)
        didOpen = True
    try:
        reader = PlistReader(pathOrFile)
        result = reader.parse()
    except NotBinaryPlistException, e:
        try:
            result = plistlib.readPlist(pathOrFile)
        except Exception, e:
            raise InvalidPlistException(e)
    if didOpen:
        pathOrFile.close()
    return result

def writePlist(rootObject, pathOrFile, binary=True):
    if not binary:
        return plistlib.writePlist(rootObject, pathOrFile)
    else:
        didOpen = False
        if isinstance(pathOrFile, (str, unicode)):
            pathOrFile = open(pathOrFile, 'w')
            didOpen = True
        writer = PlistWriter(pathOrFile, rootObject)
        result = writer.writeRoot()
        if didOpen:
            pathOrFile.close()
        return result

def readPlistFromString(data):
    return readPlist(StringIO(data))

def writePlistToString(rootObject, binary=True):
    if not binary:
        return plistlib.writePlistToString(rootObject)
    else:
        io = StringIO()
        writeRoot(rootObject, io)
        return io.getvalue()

def is_stream_binary_plist(stream):
    stream.seek(0)
    header = stream.read(7)
    if header == 'bplist0':
        return True
    else:
        return False

PlistTrailer = namedtuple('PlistTrailer', 'offsetSize, objectRefSize, offsetCount, topLevelObjectNumber, offsetTableOffset')
PlistByteCounts = namedtuple('PlistByteCounts', 'boolBytes, intBytes, realBytes, dateBytes, dataBytes, stringBytes, uidBytes, arrayBytes, setBytes, dictBytes')

class PlistReader(object):
    file = None
    contents = ''
    offsets = None
    root = None
    trailer = None
    uniques = None
    currentOffset = 0
    
    def __init__(self, fileOrStream):
        """Raises NotBinaryPlistException."""
        self.reset()
        self.file = fileOrStream
    
    def parse(self):
        return self.readRoot()
    
    def reset(self):
        self.trailer = None
        self.contents = ''
        self.offsets = []
        self.uniques = []
        self.root = None
        self.currentOffset = 0
    
    def readRoot(self):
        self.reset()
        # Get the header, make sure it's a valid file.
        if not is_stream_binary_plist(self.file):
            raise NotBinaryPlistException()
        self.file.seek(0)
        self.contents = self.file.read()
        if len(self.contents) < 32:
            raise InvalidPlistException("File is too short.")
        trailerContents = self.contents[-32:]
        try:
            self.trailer = PlistTrailer._make(unpack("!xxxxxxBBQQQ", trailerContents))
            print "trailer:", self.trailer
            offset_size = self.trailer.offsetSize * self.trailer.offsetCount
            offset = self.trailer.offsetTableOffset
            offset_contents = self.contents[offset:offset+offset_size]
            if len(offset_contents) != self.trailer.offsetCount:
                raise InvalidPlistException("Invalid offset count. Expcted %d got %d." % (self.trailer.offsetCount, len(offset_contents)))
            offset_i = 0
            while offset_i < self.trailer.offsetCount:
                tmp_contents = offset_contents[self.trailer.offsetSize*offset_i:]
                tmp_sized = self.getSizedInteger(tmp_contents, self.trailer.offsetSize)
                self.offsets.append(tmp_sized)
                offset_i += 1
            self.setCurrentOffsetToObjectNumber(self.trailer.topLevelObjectNumber)
            self.root = self.readObject()
            print self.offsets
        except TypeError, e:
            raise InvalidPlistException(e)
        print "root is:", self.root
        return self.root
    
    def setCurrentOffsetToObjectNumber(self, objectNumber):
        self.currentOffset = self.offsets[objectNumber]
    
    def readObject(self):
        result = None
        tmp_byte = self.contents[self.currentOffset:self.currentOffset+1]
        marker_byte = unpack("!B", tmp_byte)[0]
        format = (marker_byte >> 4) & 0x0f
        extra = marker_byte & 0x0f
        self.currentOffset += 1
        
        def proc_extra(extra):
            if extra == 0b1111:
                self.currentOffset += 1
                extra = self.readObject()
            return extra
        
        # bool or fill byte
        if format == 0b0000:
            if extra == 0b1000:
                result = False
            elif extra == 0b1001:
                result = True
            elif extra == 0b1111:
                pass # fill byte
            else:
                raise InvalidPlistException("Invalid object found.")
        # int
        elif format == 0b0001:
            extra = proc_extra(extra)
            result = self.readInteger(pow(2, extra))
        # real
        elif format == 0b0010:
            extra = proc_extra(extra)
            result = self.readReal(extra)
        # date
        elif format == 0b0011 and extra == 0b0011:
            result = self.readDate()
        # data
        elif format == 0b0100:
            extra = proc_extra(extra)
            result = self.readData(extra)
        # ascii string
        elif format == 0b0101:
            extra = proc_extra(extra)
            result = self.readAsciiString(extra)
        # Unicode string
        elif format == 0b0110:
            extra = proc_extra(extra)
            result = self.readUnicode(extra)
        # uid
        elif format == 0b1000:
            result = self.readUid(extra)
        # array
        elif format == 0b1010:
            extra = proc_extra(extra)
            result = self.readArray(extra)
        # set
        elif format == 0b1100:
            extra = proc_extra(extra)
            result = set(self.readArray(extra))
        # dict
        elif format == 0b1101:
            extra = proc_extra(extra)
            result = self.readDict(extra)
        else:    
            raise InvalidPlistException("Invalid object found: {format: %s, extra: %s}" % (bin(format), bin(extra)))
        return result
    
    def readInteger(self, bytes):
        result = 0
        original_offset = self.currentOffset
        data = self.contents[self.currentOffset:self.currentOffset+bytes]
        # 1, 2, and 4 byte integers are unsigned
        if bytes == 1:
            result = unpack('>B', data)[0]
        elif bytes == 2:
            result = unpack('>H', data)[0]
        elif bytes == 4:
            result = unpack('>L', data)[0]
        elif bytes == 8:
            result = unpack('>q', data)[0]
        else:
            #!! This doesn't work?
            i = 0
            while i < bytes:
                self.currentOffset += 1
                result += (result << 8) + unpack('>B', self.contents[i])[0]
                i += 1
        self.currentOffset = original_offset + bytes
        return result
    
    def readReal(self, length):
        result = 0.0
        to_read = pow(2, length)
        data = self.contents[self.currentOffset:self.currentOffset+to_read]
        if length == 2: # 4 bytes
            result = unpack('>f', data)[0]
        elif length == 3: # 8 bytes
            result = unpack('>d', data)[0]
        else:
            raise InvalidPlistException("Unknown real of length %d bytes" % to_read)
        return result
    
    def readRefs(self, count):    
        refs = []
        i = 0
        while i < count:
            fragment = self.contents[self.currentOffset:self.currentOffset+self.trailer.objectRefSize]
            ref = self.getSizedInteger(fragment, len(fragment))
            refs.append(ref)
            self.currentOffset += self.trailer.objectRefSize
            i += 1
        return refs
    
    def readArray(self, count):
        result = []
        values = self.readRefs(count)
        i = 0
        while i < len(values):
            self.setCurrentOffsetToObjectNumber(values[i])
            value = self.readObject()
            result.append(value)
            i += 1
        return result
    
    def readDict(self, count):
        result = {}
        keys = self.readRefs(count)
        values = self.readRefs(count)
        i = 0
        while i < len(keys):
            self.setCurrentOffsetToObjectNumber(keys[i])
            key = self.readObject()
            self.setCurrentOffsetToObjectNumber(values[i])
            value = self.readObject()
            result[key] = value
            i += 1
        return result
    
    def readAsciiString(self, length):
        result = unpack("!%ds" % length, self.contents[self.currentOffset:self.currentOffset+length])[0]
        self.currentOffset += length
        return result
    
    def readUnicode(self, length):
        data = self.contents[self.currentOffset:self.currentOffset+length*2]
        data = unpack(">%ds" % (length*2), data)[0]
        self.currentOffset += length * 2
        return data.decode('utf-16-be')
    
    def readDate(self):
        global apple_reference_date_offset
        result = unpack(">d", self.contents[self.currentOffset:self.currentOffset+8])[0]
        result = datetime.datetime.utcfromtimestamp(result + apple_reference_date_offset)
        self.currentOffset += 8
        return result
    
    def readData(self, length):
        result = self.contents[self.currentOffset:self.currentOffset+length]
        self.currentOffset += length
        return Data(result)
    
    def readUid(self, length):
        return Uid(self.readInteger(length+1))
    
    def getSizedInteger(self, data, intSize):
        result = 0
        i = 0
        d_read = ''
        while i < intSize:
            d_read += bin(unpack('!B', data[i])[0])
            result += (result << 8) + unpack('!B', data[i])[0]
            i += 1
        return result

class PlistWriter(object):
    file = None
    byteCounts = None
    offsets = None
    serializedUniques = None
    trailer = None
    uniques = None
    uniquePositions = None
    references = 0
    header = 'bplist00'
    trailer_size = 32
    
    def __init__(self, file):
        self.reset()
        self.file = file

    def reset(self):
        self.byteCounts = PlistByteCounts(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.offsets = []
        self.serializedUniques = ''
        self.trailer = PlistTrailer()
        self.uniques = []
        self.uniquePositions = []
        self.references = 0
        
    def writeRoot(self, root):
        """
        Strategy is:
        - write header
        - write objects
        - computer object reference length
        - write object reference positions
        - writer trailer
        """
        result = self.header
        
        
        
        
        self.computeUniquesAndOffsets(root)
        
        self.trailer.objectRefSize = self.intSize(self.references)
        ref_size = self.trailer.objectRefSize * self.references
        #!! trailer_size is uneccesary?
        file_size = sum(self.byteCounts) + ref_size + len(self.header) + self.trailer_size
        # Should write offsets after data, so shouldn't require longer length.
        self.trailer.offsetSize = self.intSize(len(file_size))
        self.trailer.offsetCount = len(self.uniques)
        self.trailer.topLevelObjectNumber = 0
        
        result = self.serializeObject(root, result)
        self.trailer.offsetTableOffset = len(result)
        result += self.serializeOffsets(self.trailer.offsetSize)
        result += pack('!xxxxxxBBQQQ', *trailer)
        
        self.file.write(result)
    
    def intSize(self, obj):
        #!! Should actually calculate size required.
        return 8

    def serializeOffsets(self, offsetSize):
        result = ''
        for offset in self.offsets:
            if offsetSize == 1:
                result += pack('>B', offset)
            elif offsetSize == 2:
                result += pack('>H', offset)
            elif offsetSize == 4:
                result += pack('>L', offset)
            elif offsetSize == 8:
                result += pack('>q', offset)
        return result

    def serializeObject(self, obj, result):    
        def proc_variable_length(format, length):
            result = ''
            if length > 0b1110:
                result += pack('!B', (format << 4) | 0b1111)
                result += self.binaryInt(length)
            else:
                result += pack('!B', (format << 4) | length)
            return result
        def proc_unique(unique):
            result = ''
            if isinstance(unique, (str, unicode, Data)):
                raise NotImplementedError("hmmm")
            else:
                raise NotImplementedError("hmmm")
            return result
        
        if type(obj) == bool:
            if obj is False:
                result += pack('!B', b00001000)
            else:
                result += pack('!B', b00001001)
        elif isinstance(obj, Uid):
            size = self.intSize(obj)
            result += pack('!B', (0b1000 << 4) | size - 1)
            result += self.binaryInt(Uid)
        elif isinstance(obj, (int, long)):
            bytes = self.intSize(obj)
            root = math.log(bytes, 2)
            result += pack('!B', (0b0001 << 4) | root)
            result += self.binaryInt(obj)
        elif isinstance(obj, float):
            # just use doubles
            result += pack('!B', (0b0010 << 4) | 3)
            result += self.binaryReal(obj)
        elif isinstance(obj, datetime.datetime):
            timestamp = time.mktime(obj.timetuple())
            timestamp -= apple_reference_date_offset
            result += pack('!B', 0b00110011)
            result += pack('!d', float(timestamp))
        elif isinstance(obj, Data):
            result += proc_variable_length(0b0100, len(obj))
            result += obj
        elif isinstance(obj, (str, unicode)):
            if isinstance(obj, unicode):
                bytes = obj.encode('utf-16be')
                result += proc_variable_length(0b0110, len(bytes))
            else:
                bytes = obj
                result += proc_variable_length(0b0101, len(bytes))
            result += bytes
        elif isinstance(obj, set):
            result += proc_variable_length(0b1100, len(obj))
            for unique in obj:
                result += proc_unique(unique)
        elif isinstance(obj, (list, tuple)):
            result += proc_variable_length(0b1010, len(obj))
            for unique in obj:
                result += proc_unique(unique)
        elif isinstance(obj, dict):
            result += proc_variable_length(0b1101, len(obj))
            keys = []
            values = []
            for key, value in obj.iteritems():
                keys.append(key)
                values.append(value)
            for key in keys:
                result += proc_unique(key)
            for value in values:
                result += proc_unique(value)
        return result
    
    def binaryReal(self, obj):
        # just use doubles
        result = pack('>d', obj)
        return result
    
    def binaryInt(self, obj):
        result = ''
        if bytes == 1:
            result += pack('>B', obj)
        elif bytes == 2:
            result += pack('>H', obj)
        elif bytes == 4:
            result += pack('>L', obj)
        elif bytes == 8:
            result += pack('>q', obj)
        else:
            #!! Uh... what to do here?
            raise NotImplementedError("Not sure how to do this yet.")
        return result

    def computeUniquesAndOffsets(self, obj):
        def proc_size(size):
            if size > 0b1110:
                size += self.intSize(size)
            return size
        
        if type(obj) == bool:
            self.byteCounts.boolBytes += 1
        elif isinstance(obj, Uid):
            size = self.intSize(obj)
            self.byteCounts.uidBytes += 1 + size
        elif isinstance(obj, (int, long)):
            size = self.intSize(obj)
            self.byteCounts.intBytes += 1 + size
        elif isinstance(obj, (float)):
            size = self.floatSize(obj)
            self.byteCounts.realBytes += 1 + size
        elif isinstance(obj, datetime.datetime):
            self.byteCounts.dateBytes += 2
        elif isinstance(obj, Data):
            if obj not in self.uniques:
                size = proc_size(len(obj))
                self.byteCounts.dataBytes += 1 + size
                self.uniques.append(obj)
        elif isinstance(obj, (str, unicode)):
            if obj not in self.uniques:
                size = proc_size(len(obj))
                self.byteCounts.stringBytes += 1 + size
                self.uniques.append(obj)
        elif isinstance(obj, set):
            size = proc_size(len(obj))
            self.byteCounts.setBytes += 1 + size
            for value in obj:
                self.references += 1
                self.computeUniquesAndOffsets(value)
        elif isinstance(obj, (list, tuple)):
            size = proc_size(len(obj))
            self.byteCounts.arrayBytes += 1 + size
            for value in obj:
                self.references += 1
                self.computeUniquesAndOffsets(value)
        elif isinstance(obj, dict):
            size = proc_size(len(obj))
            self.byteCounts.dictBytes += 1 + size
            for key, value in obj.iteritems():
                self.references += 2
                self.computeUniquesAndOffsets(key)
                self.computeUniquesAndOffsets(value)
        else:
            raise InvalidPlistException("Unknown object type.")
