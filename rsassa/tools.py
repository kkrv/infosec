import binascii
from random import randrange, getrandbits
from binascii import hexlify as hexl, unhexlify as unhexl
# from gmpy2 import is_prime
from numpy import long


def is_prime(n, k=24):
    """
    Miller-Rabin primality test.
    :param n: n to check
    :param k: number of rounds
    :return: true if n is probably prime, else false
    """
    if n == 2 or n == 3:
        return True
    if n <= 1 or n % 2 == 0:
        return False

    s = 0
    t = n - 1
    while t & 1 == 0:
        s += 1
        t //= 2

    # n-1 = t*2^s

    for _ in range(k):
        a = randrange(2, n - 1)
        x = pow(a, t, n)
        if x != 1 and x != n - 1:
            j = 1
            while j < s and x != n - 1:
                x = pow(x, 2, n)
                if x == 1:
                    return False
                j += 1
            if x != n - 1:
                return False
    return True


def generate_random_prime_candidate(length):
    p = getrandbits(length)
    p |= (1 << length - 1) | 1
    return p


def generate_random_prime_number(length=1024):
    p = 4
    while not is_prime(p):
        p = generate_random_prime_candidate(length)
    return p


def gcd_ext(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = gcd_ext(b % a, a)
        return (g, x - (b // a) * y, y)


def modinv(a, m):
    g, x, y = gcd_ext(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m


def int_bytesize(n):
    return (n.bit_length() + 7) // 8


# https://mail.python.org/pipermail/python-list/2004-July/285452.html
def i2osp(x, xLen):
    """
    Converts a nonnegative integer to an octet string of a specified length.
    :param x: nonnegative integer to be converted
    :param xLen: intended length of the resulting octet string
    :return: corresponding octet string of length xLen
    """
    if x >= pow(256, xLen):
        raise Exception('integer is too large')

    h = hex(x)[2:]  # remove 0x prefix
    if h[-1:] == 'L':
        h = h[:-1]  # remove L suffix if present
    if len(h) & 1:
        h = "0" + h
    h = unhexl(h)
    return b'\x00' * int(xLen-len(h)) + h


def os2ip(s):
    """
    Converts an octet string to a nonnegative integer.
    :param s: octet string to be converted
    :return: corresponding nonnegative integer
    """
    return int(hexl(s), 16)


if __name__ == '__main__':
    n = 238955575675875883
    print(i2osp(n, 10))