from hashing.sha3 import sha3 as sha
from rsassa.tools import *


sha_3_256_pad = b'\x30\x31\x30\x0d\x06\x09\x60\x86\x48\x01\x65\x03\x04\x02\x08\x05\x00\x04\x20'


class RSASSA_PKCS:
    def __init__(self):
        self.p = generate_random_prime_number(256)
        self.q = generate_random_prime_number(256)

        self.n = self.p * self.q
        self.phi_n = (self.p - 1) * (self.q - 1)

        self.e = 65537
        self.__d = modinv(self.e, self.phi_n)

    def get_public_key(self):
        return {
            'n': self.n,
            'e': self.e
        }

    def sign(self, message):
        # signature = self.encrypt(message, k=128)
        k = int_bytesize(self.n)
        em = self._eme_encoding(message, k)
        m = os2ip(em)
        c = self._rsaep(m, self.get_public_key())
        return {
            'message': message,
            'signature': i2osp(c, k)
        }

    def verify(self, signature, public_key):
        s = signature['signature']
        k = int_bytesize(public_key['n'])
        c = os2ip(s)
        m = self._rsadp(c)
        em = i2osp(m, k)
        em2 = self._eme_encoding(signature['message'], k)
        if em == em2:
            return True
        else:
            return False

    def _eme_encoding(self, m, k):
        h = bytes.fromhex(sha(m))  # from hexstring to bytes
        if len(h) > k - 11:
            raise Exception('message is too long')
        t = sha_3_256_pad + h
        ps_len = k - len(t) - 3
        ps = b'\xff' * ps_len
        return b'\x00\x01' + ps + b'\x00' + t

    def _rsaep(self, m, public_key):
        """
        :param message: imput message
        :return: c ciphertext representative, an integer between 0 and n - 1
        """
        if not 0 < m < self.n - 1:
            raise Exception('message representative out of range')
        return pow(m, public_key['e'], public_key['n'])

    def _rsadp(self, c):
        """
        :param c: ciphertext representative, an integer between 0 and n - 1
        :return: message representative, an integer between 0 and n - 1
        """
        if not 0 < c < self.n - 1:
            raise Exception('cipher text representative out of range')
        return pow(c, self.__d, self.n)


if __name__ == '__main__':
    m = 'Karina'
    rsa = RSASSA_PKCS()

    pub_key = rsa.get_public_key()

    signature = rsa.sign(m)
    print(signature)
    print(rsa.verify(signature, pub_key))
