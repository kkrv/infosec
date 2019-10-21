from rsassa.tools import *
from hashing.sha3 import sha3 as sha


class RSASSA:
    def __init__(self):
        self.p = generate_random_prime_number(256)
        self.q = generate_random_prime_number(256)

        self.n = self.p * self.q
        self.phi_n = (self.p - 1) * (self.q - 1)

        self.e = 65537
        self.__d = modinv(self.e, self.phi_n)

    def get_public_key(self):
        return self.e

    def sign(self, message):
        hash = int(sha(message), 16)
        return {'message': message, 'signature': hex(pow(hash, self.__d, self.n))}

    def verify(self, signature, public_key):
        message = signature['message']
        hash = int(sha(message), 16)
        decrypted_hash = pow(int(signature['signature'], 16), public_key, self.n)
        return decrypted_hash == hash
