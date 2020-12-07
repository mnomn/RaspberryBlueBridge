import unittest

from rbb import listener


def test_short():
    aaa = "aaa"
    assert(len(aaa) > 0)
    elements = [0xCC, 00]
    a = listener.convert_bytes_to_signed(elements)
    assert(a > 0)
