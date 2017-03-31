import unittest

from chconsole.messages import filter_meta, process_command_meta, is_command_meta
from chconsole.messages import UserJoin, UserLeave

__author__ = 'minimair'


class Tester(unittest.TestCase):
    def setUp(self):
        self.s = '#abc/{"type": "command", "content":{"user": "join"}}'
        self.t = '#abc/{"type": "command", "content":{"user": "leave"}}'
        self.u = '#abc/{"type": "command", "content":{"user": "other"}}'
        pass

    def tearDown(self):
        pass

    def test_filter0(self):
        instruction = filter_meta('abc', self.s)
        # print('instruction: ', instruction)
        # res = is_command_meta(instruction)
        processed = process_command_meta(instruction, 'fred')
        # print('processed', processed.username)
        res = isinstance(processed, UserJoin) and processed.username == 'fred'
        # print('result', res)
        self.assertEqual(res, True)

    def test_filter1(self):
        instruction = filter_meta('abc', self.t)
        processed = process_command_meta(instruction, 'fred')
        res = isinstance(processed, UserLeave) and processed.username == 'fred'
        self.assertEqual(res, True)

    def test_filter2(self):
        instruction = filter_meta('abc', self.u)
        processed = process_command_meta(instruction, 'fred')
        res = processed == None
        self.assertEqual(res, True)


if __name__ == '__main__':
    unittest.main()
