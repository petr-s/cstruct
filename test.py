#!/usr/bin/env python

__license__ = """
The MIT License (MIT)

Copyright (c) 2014 Petr Skramovsky (petr.skramovsky[at]gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

__author__ = "Petr Skramovsky"

__version__ = "0.1"

import unittest
from cstruct import *
from StringIO import StringIO


class Test(unittest.TestCase):

    def testAttributesOrder(self):
        class TestStruct(Struct):
            z = Int()
            a = String(10)
            d = Short()
            c = Int()
        self.assertEqual(0, TestStruct.z.index)
        self.assertEqual(1, TestStruct.a.index)
        self.assertEqual(2, TestStruct.d.index)
        self.assertEqual(3, TestStruct.c.index)

    def testEndianRead(self):
        class TestStruct(Struct):
            a = Int()
        Struct.ENDIAN = Endian.LITTLE
        fo = self._bytes2file([0x2A, 0x00, 0x00, 0x00])
        test = TestStruct().read(fo)
        self.assertEqual(42, test.a)
        Struct.ENDIAN = Endian.BIG
        fo = self._bytes2file([0x00, 0x00, 0x00, 0x2A])
        test = TestStruct().read(fo)
        self.assertEqual(42, test.a)
        Struct.ENDIAN = Endian.LITTLE

    def testEndianWrite(self):
        class TestStruct(Struct):
            a = Int()
        fo = self._emptyFile()
        Struct.ENDIAN = Endian.LITTLE
        test = TestStruct().set(42)
        test.write(fo)
        data = self._file2bytes(fo)
        self.assertEqual([0x2A, 0x00, 0x00, 0x00], data)
        Struct.ENDIAN = Endian.BIG
        fo = self._emptyFile()
        test.write(fo)
        data = self._file2bytes(fo)
        self.assertEqual([0x00, 0x00, 0x00, 0x2A], data)
        Struct.ENDIAN = Endian.LITTLE

    def testBoolRead(self):
        class TestStruct(Struct):
            a = Bool()
        fo = self._bytes2file([0x01])
        test = TestStruct().read(fo)
        self.assertEqual(True, test.a)

    def testCharRead(self):
        class TestStruct(Struct):
            a = Char()
        fo = self._bytes2file([0xD6])
        test = TestStruct().read(fo)
        self.assertEqual(-42, test.a)

    def testUnsignedCharRead(self):
        class TestStruct(Struct):
            a = UnsignedChar()
        fo = self._bytes2file([0x2A])
        test = TestStruct().read(fo)
        self.assertEqual(42, test.a)

    def testShortRead(self):
        class TestStruct(Struct):
            a = Short()
        fo = self._bytes2file([0xD6, 0xFF])
        test = TestStruct().read(fo)
        self.assertEqual(-42, test.a)

    def testUnsignedShortRead(self):
        class TestStruct(Struct):
            a = UnsignedShort()
        fo = self._bytes2file([0x2A, 0x00])
        test = TestStruct().read(fo)
        self.assertEqual(42, test.a)

    def testIntRead(self):
        class TestStruct(Struct):
            a = Int()
        fo = self._bytes2file([0xD6, 0xFF, 0xFF, 0xFF])
        test = TestStruct().read(fo)
        self.assertEqual(-42, test.a)

    def testUnsignedIntRead(self):
        class TestStruct(Struct):
            a = UnsignedInt()
        fo = self._bytes2file([0x2A, 0x00, 0x00, 0x00])
        test = TestStruct().read(fo)
        self.assertEqual(42, test.a)

    def testFloatRead(self):
        class TestStruct(Struct):
            a = Float()
        fo = self._bytes2file([0xC3, 0xF5, 0x48, 0x40])
        test = TestStruct().read(fo)
        self.assertAlmostEqual(3.14, test.a, delta=0.000001)

    def testSimpleRead(self):
        class TestStruct(Struct):
            a = Int()
            b = UnsignedShort(2)
        fo = self._bytes2file([0x2A, 0x00, 0x00, 0x00, 0x01, 0x00, 0x02, 0x00])
        test = TestStruct().read(fo)
        self.assertEqual(42, test.a)
        self.assertEqual([1, 2], test.b)

    def testReadTrimString(self):
        class TestStruct(Struct):
            a = String(8)
        fo = self._bytes2file([0x68, 0x65, 0x6C, 0x6C, 0x6F, 0x00, 0x01, 0x01])
        test = TestStruct().read(fo)
        self.assertEqual("hello", test.a)

    def testReadStructInStruct(self):
        class TestStruct(Struct):
            a = Int()

        class TestStruct2(Struct):
            a = TestStruct(2)
            b = Int()
        fo = self._bytes2file([0x2A, 0x00, 0x00, 0x00, 0x2B, 0x00, 0x00, 0x00,
                               0x01, 0x00, 0x00, 0x00])
        test = TestStruct2().read(fo)
        self.assertEqual(42, test.a[0].a)
        self.assertEqual(43, test.a[1].a)
        self.assertEqual(1, test.b)

    def testSimpleWrite(self):
        class TestStruct(Struct):
            a = Int()
            b = UnsignedShort(2)
        fo = self._emptyFile()
        test = TestStruct().set(42, [1, 2])
        test.write(fo)
        data = self._file2bytes(fo)
        self.assertEqual([0x2A, 0x00, 0x00, 0x00], data[:4])
        self.assertEqual([0x01, 0x00, 0x02, 0x00], data[4:])

    def testWriteStructInStruct(self):
        class TestStruct(Struct):
            a = Int()

        class TestStruct2(Struct):
            a = TestStruct()
            b = Int()
        fo = self._emptyFile()
        test = TestStruct2()
        test.a = TestStruct().set(42)
        test.b = 1
        test.write(fo)
        data = self._file2bytes(fo)
        self.assertEqual([0x2A, 0x00, 0x00, 0x00], data[:4])
        self.assertEqual([0x01, 0x00, 0x00, 0x00], data[4:])

    def testWriteStrucArraytInStruct(self):
        class TestStruct(Struct):
            a = Int()

        class TestStruct2(Struct):
            a = TestStruct(2)
            b = Int()
        fo = self._emptyFile()
        test = TestStruct2()
        test.a = [TestStruct().set(42), TestStruct().set(43)]
        test.b = 1
        test.write(fo)
        data = self._file2bytes(fo)
        self.assertEqual([0x2A, 0x00, 0x00, 0x00], data[:4])
        self.assertEqual([0x2B, 0x00, 0x00, 0x00], data[4:8])
        self.assertEqual([0x01, 0x00, 0x00, 0x00], data[8:])

    def _bytes2file(self, data):
        return StringIO("".join([chr(x) for x in data]))

    def _file2bytes(self, fo):
        return [ord(c) for c in fo.getvalue()]

    def _emptyFile(self):
        return StringIO()

if __name__ == "__main__":
    unittest.main()
