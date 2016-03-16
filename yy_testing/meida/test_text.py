import unittest

from media import is_comment, to_comment, de_comment

__author__ = 'minimair'


class Tester(unittest.TestCase):
    def setUp(self):
        self.s = '  # hello'
        self.t = '# hi'
        self.u = 'hi'
        self.a = 'a\nb'
        self.b = 'a#b'
        self.c = '#a\\\n#b\n#c'
        pass

    def tearDown(self):
        pass

    def test_is0(self):
        res = is_comment(self.s)
        self.assertEqual(res, True)

    def test_is1(self):
        res = is_comment(self.t)
        self.assertEqual(res, True)

    def test_is2(self):
        res = is_comment(self.u)
        self.assertEqual(res, False)

    def test_to0(self):
        res = to_comment(self.a)
        self.assertEqual(res, '#a\n#b')

    def test_de0(self):
        res = de_comment(self.s)
        self.assertEqual(res, '   hello')

    def test_de1(self):
        res = de_comment(self.t)
        self.assertEqual(res, ' hi')

    def test_de2(self):
        res = de_comment(self.u)
        self.assertEqual(res, 'hi')

    def test_de3(self):
        res = de_comment(self.a)
        self.assertEqual(res, 'a\nb')

    def test_de4(self):
        res = de_comment(self.b)
        self.assertEqual(res, 'a#b')

    def test_de5(self):
        res = de_comment(self.c)
        self.assertEqual(res, 'a\nb\nc')

if __name__ == '__main__':
    unittest.main()

# issue
# aaa
# bbb