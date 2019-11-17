import unittest
from rsassa.rsa import RSASSA


class TestRSADigSign(unittest.TestCase):
    def test_empty(self):
        rsa_dig_singature = RSASSA()
        self.assertTrue(rsa_dig_singature.verify(rsa_dig_singature.sign(''), rsa_dig_singature.get_public_key()))

    def test_t(self):
        rsa_dig_singature = RSASSA()
        self.assertTrue(rsa_dig_singature.verify(rsa_dig_singature.sign('Karina'), rsa_dig_singature.get_public_key()))

    def test_f(self):
        rsa_dig_singature = RSASSA()
        sign = rsa_dig_singature.sign('Hello')
        sign['message'] = 'Hello there'
        self.assertFalse(rsa_dig_singature.verify(sign, rsa_dig_singature.get_public_key()))


if __name__ == '__main__':
    unittest.main()
