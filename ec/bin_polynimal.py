from copy import copy


class BinaryPolynomial:
    def __init__(self, p):
        self.p = p

    def __str__(self):
        unicode = False
        sup = lambda s: "".join("⁰¹²³⁴⁵⁶⁷⁸⁹"[ord(c) & 0xF] for c in s)
        power = lambda s: 'x' + sup(s) if unicode else 'x' + "^" + s
        term = lambda bit: '1' if bit == 0 else ('x' if bit == 1 else power(str(bit)))
        return ' + '.join(map(term, sorted(self.to_bits(self.p), reverse=True)))

    def __eq__(self, other):
        return self.p == other.p

    def __ne__(self, other):
        return self.p != other.p

    def __add__(self, other):
        return BinaryPolynomial(self.p ^ other.p)

    def __sub__(self, other):
        return BinaryPolynomial(self.p ^ other.p)

    def __mul__(self, other):
        this = copy(self.p)
        other = other.p
        result = 0
        while this and other:
            if this & 1:
                result ^= other
            this >>= 1
            other <<= 1
        return BinaryPolynomial(result)

    def __pow__(self, power, modulo=None):
        factor = copy(self)
        factor = factor % modulo if modulo else factor
        result = BinaryPolynomial(1)
        while power:
            if power & 1:
                result = result.mulmod(factor, modulo) if modulo else result * factor
            factor = factor.mulmod(factor, modulo) if modulo else factor * factor
            power >>= 1
        return result

    def mulmod(self, other, modulo):
        """
        :return: self * other % modulo
        """
        result = 0
        deg = modulo.p.bit_length() - 1
        assert (other.p.bit_length() - 1) < deg
        this = copy(self.p)
        other = other.p
        modulo = modulo.p
        while this and other:
            if this & 1:
                result ^= other
            this >>= 1
            other <<= 1
            if (other >> deg) & 1:
                other ^= modulo
        return BinaryPolynomial(result)

    def __floordiv__(self, other):
        """
        :return: [x/y]
        """
        return divmod(self, other)[0]

    def __divmod__(self, other):
        """
        Binary polynomial division.
        :param other: BinaryPolynomail (divider)
        :return: (quotient, remainder) polynomials
        """
        q = 0
        bl = other.p.bit_length()
        this = copy(self.p)
        other = other.p
        while True:
            shift = this.bit_length() - bl
            if shift < 0:
                return (BinaryPolynomial(q), BinaryPolynomial(this))
            q ^= 1 << shift
            this ^= other << shift

    def __mod__(self, other):
        a = copy(self.p)
        other = other.p
        bl = other.bit_length()
        while True:
            shift = a.bit_length() - bl
            if shift < 0:
                return BinaryPolynomial(a)
            a ^= other << shift

    def modinv(self, m):
        g, x, y = BinaryPolynomial.egcd(copy(self), m)
        if g != 1:
            raise Exception('modular inverse does not exist')
        else:
            return BinaryPolynomial(x)

    def gcd(self, b):
        a = copy(self)
        while b:
            a, b = b, a % b
        return a

    @staticmethod
    def egcd(a, b):
        """
        mul(a,x) ^ mul(b,y) = d
        :return: (d, x, y) where d is the Greatest Common Divisor of polynomials a and b.
        """
        a = (a.p, 1, 0)
        b = (b.p, 0, 1)
        while True:
            q, r = BinaryPolynomial.i_divmod(a[0], b[0])
            if not r:
                return b
            a, b = b, (r, a[1] ^ (BinaryPolynomial(q) * BinaryPolynomial(b[1])).p,
                       a[2] ^ (BinaryPolynomial(q) * BinaryPolynomial(b[2])).p)

    @staticmethod
    def to_bits(n):
        bits = set()
        bit = 0
        while n:
            if n & 1:
                bits.add(bit)
            bit += 1
            n >>= 1
        return bits

    @staticmethod
    def from_bits(bits):
        n = 0
        for bit in bits:
            n |= 1 << bit
        return n

    @staticmethod
    def i_divmod(a, b):
        q = 0
        bl = b.bit_length()
        while True:
            shift = a.bit_length() - bl
            if shift < 0:
                return (q, a)
            q ^= 1 << shift
            a ^= b << shift


if __name__ == '__main__':
    a = BinaryPolynomial(1676956011799388130109086516981802144450075144559)
    b = BinaryPolynomial(0b000010)
    f = BinaryPolynomial(int("".join(str(i) for i in ([1 if j in (163, 7, 6, 3, 1) else 0 for j in range(163, 0, -1)])), 2))
    c = a.modinv(f)
    print(a.mulmod(c, f))
