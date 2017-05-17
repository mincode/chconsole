import unittest

from chconsole.tab import UserClient
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
        self.s.insert('bb', '0')
        res = self.s.users
        self.assertEqual(res[0], UserClient('bb', ['0']))

    def test_2(self):
        self.s.insert('bb', '0')
        self.s.insert('bb', '0')
        res = self.s.users
        self.assertEqual(res[0], UserClient('bb', ['0']))

    def test_3(self):
        self.s.insert('bb', '0')
        self.s.insert('bb', '1')
        res = self.s.users
        self.assertEqual(res[0], UserClient('bb', ['0', '1']))

    def test_4(self):
        self.s.insert('aa', '0')
        self.s.insert('bb', '1')
        res = self.s.users
        self.assertEqual(res, [UserClient('aa', ['0']), UserClient('bb', ['1'])])

    def test_5(self):
        self.s.insert('bb', '1')
        self.s.insert('aa', '0')
        res = self.s.users
        self.assertEqual(res, [UserClient('aa', ['0']), UserClient('bb', ['1'])])

    def test_6(self):
        self.s.insert('bb', '1')
        self.s.insert('aa', '0')
        self.s.insert('ab', '2')
        res = self.s.users
        self.assertEqual(res, [UserClient('aa', ['0']), UserClient('ab', ['2']), UserClient('bb', ['1'])])

    def test_7(self):
        self.s.insert('bb', '1')
        self.s.insert('aa', '0')
        self.s.insert('ab', '2')
        self.s.remove('cc', '3')
        res = self.s.users
        self.assertEqual(res, [UserClient('aa', ['0']), UserClient('ab', ['2']), UserClient('bb', ['1'])])

    def test_8(self):
        self.s.insert('bb', '1')
        self.s.insert('aa', '0')
        self.s.insert('ab', '2')
        self.s.remove('aa', '0')
        res = self.s.users
        self.assertEqual(res, [UserClient('ab', ['2']), UserClient('bb', ['1'])])

    def test_9(self):
        self.s.insert('bb', '1')
        self.s.insert('aa', '0')
        self.s.insert('ab', '2')
        self.s.insert('aa', '3')
        self.s.remove('aa', '0')
        res = self.s.users
        self.assertEqual(res, [UserClient('aa', ['3']), UserClient('ab', ['2']), UserClient('bb', ['1'])])

if __name__ == '__main__':
    unittest.main()
