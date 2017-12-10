import unittest
from chconsole.connect.curie import Curie

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Tester(unittest.TestCase):
    def setUp(self):
        self.c1 = 'machine/key'
        self.c2 = self.c1 + '/aba'
        self.b1 = '[' + self.c1
        self.b2 = self.c1 + ']'
        self.b3 = '[' + self.c1 + ']'
        self.d1 = '[' + self.c2
        self.d2 = self.c2 + ']'
        self.d3 = '[' + self.c2 + ']'

        pass

    def tearDown(self):
        pass

    def test_split_curie0(self):
        c = Curie(self.c1)
        res = [c.machine, c.key]
        self.assertEqual(res, ['machine', 'key'])

    def test_split_curie1(self):
        c = Curie(self.b1)
        res = [c.machine, c.key]
        self.assertEqual(res, ['machine', 'key'])

    def test_split_curie2(self):
        c = Curie(self.b2)
        res = [c.machine, c.key]
        self.assertEqual(res, ['machine', 'key'])

    def test_split_curie3(self):
        c = Curie(self.b3)
        res = [c.machine, c.key]
        self.assertEqual(res, ['machine', 'key'])

    def test_split_curie4(self):
        c = Curie(self.c2)
        res = [c.machine, c.key]
        self.assertEqual(res, ['machine', 'key/aba'])

    def test_split_curie5(self):
        c = Curie(self.d1)
        res = [c.machine, c.key]
        self.assertEqual(res, ['machine', 'key/aba'])

    def test_split_curie6(self):
        c = Curie(self.d2)
        res = [c.machine, c.key]
        self.assertEqual(res, ['machine', 'key/aba'])

    def test_split_curie7(self):
        c = Curie(self.d3)
        res = [c.machine, c.key]
        self.assertEqual(res, ['machine', 'key/aba'])


if __name__ == '__main__':
    unittest.main()
