import unittest
from ec.bin_polynimal import BinaryPolynomial as BP
from ec.point import Point


class TestArithmetic(unittest.TestCase):

    def test_mulmod(self):
        a = BP(0b001101)
        b = BP(0b101011)
        f = BP(0b1000011)
        res = BP(0b010110)
        self.assertEqual(a.mulmod(b, f), res)

    def test_egcd(self):
        # return: (d, x, y)
        # mul(a, x) ^ mul(b, y) = d
        a = BP(0b001101)
        b = BP(0b1000011)
        d, x, y = BP.egcd(a, b)
        self.assertEqual(a*BP(x) + b*BP(y), BP(d))

    def test_modinv(self):
        a = BP(0b001101)
        b = BP(0b1000011)
        c = a.modinv(b)
        self.assertEqual(a.mulmod(c, b), BP(0b01))


class TestEC(unittest.TestCase):

    def test_random_point_generation(self):
        a = Point.generate_point()
        self.assertTrue(a.is_on_curve())

    def test_points_add(self):
        a = Point.generate_point()
        b = Point.generate_point()
        c = a + b
        self.assertTrue(c.is_on_curve())

    def test_point_double(self):
        a = Point.generate_point()
        b = a + a
        self.assertTrue(b.is_on_curve())

    def test_point_mul(self):
        a = Point.generate_point()
        k = 221
        self.assertTrue(a.mul(k).is_on_curve())


if __name__ == '__main__':
    unittest.main()
