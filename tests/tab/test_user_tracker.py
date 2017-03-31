import unittest

from chconsole.tab import UserTracker

__author__ = 'minimair'


class Tester(unittest.TestCase):
    def setUp(self):
        self.s = UserTracker()
        pass

    def tearDown(self):
        pass

    def test_0(self):
        res = self.s.users
        self.assertEqual(res, [])

    def test_1(self):
        self.s.insert('bb')
        res = self.s.users
        self.assertEqual(res, ['bb'])

    def test_2(self):
        self.s.insert('bb')
        self.s.insert('bb')
        res = self.s.users
        self.assertEqual(res, ['bb'])

    def test_3(self):
        self.s.insert('aa')
        self.s.insert('bb')
        res = self.s.users
        self.assertEqual(res, ['aa', 'bb'])

    def test_4(self):
        self.s.insert('bb')
        self.s.insert('aa')
        res = self.s.users
        self.assertEqual(res, ['aa', 'bb'])

    def test_5(self):
        self.s.insert('bb')
        self.s.insert('aa')
        self.s.insert('ab')
        res = self.s.users
        self.assertEqual(res, ['aa', 'ab', 'bb'])

    def test_6(self):
        self.s.insert('bb')
        self.s.insert('aa')
        self.s.insert('ab')
        self.s.remove('cc')
        res = self.s.users
        self.assertEqual(res, ['aa', 'ab', 'bb'])

    def test_7(self):
        self.s.insert('bb')
        self.s.insert('aa')
        self.s.insert('ab')
        self.s.remove('aa')
        res = self.s.users
        self.assertEqual(res, ['ab', 'bb'])

if __name__ == '__main__':
    unittest.main()
