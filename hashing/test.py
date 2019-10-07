import unittest

from sha3 import sha3
from sha2 import sha2


class TestSHA2(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(sha2(''),
                         '6a09e667bb67ae853c6ef372a54ff53a510e527f9b05688c1f83d9ab5be0cd19')

    def test_m(self):
        self.assertEqual(sha2('The quick brown fox jumps over the lazy dog'),
                         'd7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592')


class TestSHA3(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(sha3(''),
                         'a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a')

    def test_m(self):
        self.assertEqual(sha3('aaa'),
                         '44f81da38e6f353c8271e090d202865d140397b7094b1087e0b11afe953650bf')


if __name__ == '__main__':
    unittest.main()
