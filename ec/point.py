from copy import copy
from random import getrandbits

from ec.bin_polynimal import BinaryPolynomial as BP


class Point:
    # y*y + x*y = x*x*x + A*x*x + B
    # f(x) = x**163 + x**7 + x**6 + x**3 + 1
    A = BP(0b1)
    B = BP(0x5FF6108462A2DC8210AB403925E638A19C1455D21)
    m = 163
    f = BP(int("".join(str(i) for i in ([1 if j in (163, 7, 6, 3, 0) else 0 for j in range(m, -1, -1)])), 2))

    def __init__(self, x=BP(0), y=BP(0)):
        self.x = x
        self.y = y

    def __str__(self):
        return '{\n\tx: ' + str(self.x) + '\n\ty: ' + str(self.y) + '\n}'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        if self.x != other.x:
            return self.add(other)
        if self.y == other.y:
            return self.double()
        return Point(BP(0), BP(0))

    def add(self, other):
        l = (self.y + other.y) * (self.x + other.x).modinv(self.f)
        x3 = (l * l % Point.f + l + self.x + other.x + self.A) % Point.f
        y3 = (l * (self.x + x3) % Point.f + x3 + self.y) % Point.f
        return Point(x3, y3)

    def double(self):
        # m = self.x + self.y.mulmod(self.x.modinv(Point.f), Point.f)  # x + y/x
        # x3 = pow(m, 2, Point.f) + m + Point.A
        # y3 = pow(x3, 2, Point.f) + (m + BP(0b01)).mulmod(x3, Point.f)
        x3 = pow(self.x, 2, Point.f) + Point.B.mulmod(pow(self.x.modinv(Point.f), 2, Point.f), Point.f)
        y3 = pow(self.x, 2, Point.f) + (self.x + self.y.mulmod(self.x.modinv(Point.f), Point.f)).mulmod(x3,
                                                                                                        Point.f) + x3
        return Point(x3, y3)

    def mul(self, k: int):
        res = copy(self)
        p = copy(self)
        k = k - 1
        while k != 0:
            if (k % 2) != 0:
                if (res.x == p.x) or (res.y == p.y):
                    res = res.double()
                else:
                    res = res + p
                k = k - 1
            k = k // 2
            p = p.double()
        return res

    def is_on_curve(self):
        return ((self.y * self.y + self.x * self.y) % self.f) == \
               ((self.x * self.x * self.x + self.A * self.x * self.x + self.B) % self.f)

    @staticmethod
    def generate_point():
        k = 0
        while k <= 0:
            u = BP(getrandbits(Point.m))
            w = pow(u, 3, Point.f) + Point.A * u * u % Point.f + Point.B
            k, z = Point.solve_sq_eq(u, w)
        return Point(u, z)

    @staticmethod
    def trace(x):
        res = copy(x)
        for i in range(Point.m - 1):
            res = pow(res, 2, Point.f) + x
        return res

    @staticmethod
    def half_trace(x):
        res = copy(x)
        for i in range(0, (Point.m - 1) // 2):
            res = pow(res, 4, Point.f) + x
        return res

    @staticmethod
    def solve_sq_eq(u: BP, w: BP):
        if u == BP(0):
            z = pow(w, pow(2, Point.m - 1, Point.f))
            k = 1
            return (k, z)

        elif w == BP(0):
            z = BP(0)
            k = 2
            return (k, z)

        else:
            try:
                inv_u = u.modinv(Point.f)
                v = w * inv_u * inv_u % Point.f
                tr_v = Point.trace(v)

                if tr_v == BP(1):
                    k = 0
                    z = BP(0)
                    return (k, z)

                else:
                    htr_v = Point.half_trace(v)
                    z = htr_v.mulmod(u, Point.f)
                    k = 2
                    return (k, z)

            except Exception:
                return (0, BP(0))


if __name__ == '__main__':
    a = Point.generate_point()
    print("point: {} is on curve: {}".format(a, a.is_on_curve()))
    b = Point.generate_point()
    print("point: {} is on curve: {}".format(b, b.is_on_curve()))
    c = a + b
    print("point: {} is on curve: {}".format(c, c.is_on_curve()))
    d = a + a
    print("point: {} is on curve: {}".format(d, d.is_on_curve()))
    e = a.mul(6)
    print("point: {} is on curve: {}".format(e, e.is_on_curve()))
