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

import inspect
from copy import deepcopy
from struct import calcsize, unpack, pack


def _enum(**args):
    return type("Enum", (object,), args)


class Attribute(object):
    _counter = 0

    def __init__(self, quantity=1):
        assert quantity > 0
        self._quantity = quantity
        self.index = Attribute._counter
        Attribute._counter += 1

    def __len__(self):
        return calcsize(self.format)

    def _alter(self, value):
        return value

    @property
    def _format(self):
        pass

    @property
    def format(self):
        return "%d%s" % (self._quantity, self._format)


class Char(Attribute):

    @property
    def _format(self):
        return "b"


class UnsignedChar(Attribute):

    @property
    def _format(self):
        return "B"


class Bool(Attribute):

    @property
    def _format(self):
        return "?"


class Short(Attribute):

    @property
    def _format(self):
        return "h"


class UnsignedShort(Attribute):

    @property
    def _format(self):
        return "H"


class Int(Attribute):

    @property
    def _format(self):
        return "i"


class UnsignedInt(Attribute):

    @property
    def _format(self):
        return "I"


class LongLong(Attribute):

    @property
    def _format(self):
        return "q"


class UnsignedLongLong(Attribute):

    @property
    def _format(self):
        return "Q"


class Float(Attribute):

    @property
    def _format(self):
        return "f"


class Double(Attribute):

    @property
    def _format(self):
        return "d"


class String(Attribute):

    @property
    def _format(self):
        return "s"

    def _alter(self, value):
        return value.split("\x00")[0]


class StructMeta(type):
    def __new__(self, classname, bases, classDict):
        cls = type.__new__(self, classname, bases, classDict)
        attrs = inspect.getmembers(cls,
                lambda attr: isinstance(attr, Attribute))
        cls._attrs = sorted(attrs, key=lambda attr: attr[1].index)
        Attribute._counter = 0
        return cls


Endian = _enum(LITTLE="<", BIG=">")


class Struct(Attribute):
    __metaclass__ = StructMeta
    ENDIAN = Endian.LITTLE

    def set(self, *values):
        for attr, value in zip(self._attrs, values):
            setattr(self, attr[0], value)
        return self

    def read(self, fo, extra=None):
        for attr in self._attrs:
            self._read_attr(attr[1], extra)
            if isinstance(attr[1], Struct):
                value = [deepcopy(attr[1].read(fo, extra))
                         for x in xrange(attr[1]._quantity)]
            else:
                value = unpack(Struct.ENDIAN + attr[1].format,
                               fo.read(len(attr[1])))
            setattr(self, attr[0], attr[1]._alter(value[0] if
                        attr[1]._quantity == 1 or
                        type(attr[1]) == String else list(value)))
        return self

    def _read_attr(self, attr, extra):
        pass

    def write(self, fo):
        for attr in self._attrs:
            if isinstance(attr[1], Struct):
                value = getattr(self, attr[0])
                for x in iter(value if isinstance(value, list) else [value]):
                    x.write(fo)
                continue
            if attr[1]._quantity == 1:
                fo.write(pack(Struct.ENDIAN + attr[1].format,
                              getattr(self, attr[0])))
            else:
                fo.write(pack(Struct.ENDIAN + attr[1].format,
                              *getattr(self, attr[0])))
