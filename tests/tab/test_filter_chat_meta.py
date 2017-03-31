import unittest

from chconsole.messages import filter_meta

__author__ = 'minimair'


class Tester(unittest.TestCase):
    def setUp(self):
        self.s = '#abc/{}'
        self.t = '#abc/{"type": "command", "content":{"user": "join"}}'
        self.u = '#abc/'
        pass

    def tearDown(self):
        pass

    def test_filter0(self):
        res = filter_meta('abc', self.s)
        self.assertEqual(res, {})

    def test_filter1(self):
        res = filter_meta('abc', self.t)
        self.assertEqual(res, {"type": "command", "content":{"user": "join"}})

    def test_filter2(self):
        res = filter_meta('abd', self.s)
        self.assertEqual(res, None)

    def test_filter3(self):
        res = filter_meta('abd', self.t)
        self.assertEqual(res, None)

    def test_filter4(self):
        res = filter_meta('abc', self.u)
        self.assertEqual(res, None)

    def test_filter5(self):
        res = filter_meta('abd', self.u)
        self.assertEqual(res, None)

if __name__ == '__main__':
    unittest.main()
