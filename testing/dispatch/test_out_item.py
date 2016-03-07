import unittest
from dispatch.import_item import _split_lines

__author__ = 'minimair'


class Tester(unittest.TestCase):
    s0 = 'ab\ncd\nef'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_zero_lines(self):
        res = _split_lines(self.s0, 0)
        self.assertEqual(res[0], 0)
        self.assertEqual(res[1], '')
        self.assertEqual(res[2], self.s0)

    def test_short(self):
        res = _split_lines(self.s0, 10)
        # print(res[0])
        self.assertEqual(res[0], 3)
        self.assertEqual(res[1], self.s0)
        self.assertEqual(res[2], '')

    def test_part(self):
        res = _split_lines(self.s0, 2)
        self.assertEqual(res[0], 2)
        self.assertEqual(res[1], 'ab\ncd\n')
        self.assertEqual(res[2], 'ef')

    def test_all(self):
        res = _split_lines(self.s0, 3)
        self.assertEqual(res[0], 3)
        self.assertEqual(res[1], 'ab\ncd\nef')
        self.assertEqual(res[2], '')

    def test_all2(self):
        t = self.s0 + '\n'
        res = _split_lines(t, 3)
        self.assertEqual(res[0], 3)
        self.assertEqual(res[1], 'ab\ncd\nef\n')
        self.assertEqual(res[2], '')

if __name__ == '__main__':
    unittest.main()
