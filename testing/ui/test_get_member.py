import unittest

from ui.tab.tab_content import get_member

__author__ = 'minimair'


class A:
    def a(self):
        return 0


class B:
    a_mem = A()

    def b(self):
        return 1


class Tester(unittest.TestCase):
    a_obj = None
    b_obj = None

    def setUp(self):
        self.a_obj = A()
        self.b_obj = B()

    def tearDown(self):
        pass

    def test_direct(self):
        res = get_member(self.a_obj, 'a')
        self.assertEqual(res(), 0)

    def test_inside(self):
        res = get_member(self.b_obj, 'a_mem.a')
        self.assertEqual(res(), 0)


if __name__ == '__main__':
    unittest.main()
