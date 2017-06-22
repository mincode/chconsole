import unittest

from chconsole.messages.meta_command import json_meta_command

__author__ = 'minimair'


class Tester(unittest.TestCase):
    def setUp(self):
        self.s = '#abc/{}'
        self.t = '#abc/{"recipient_client_id": "ai", "recipient": "aa"' + \
                 ', "sender_client_id": "bi", "sender": "bb"' + \
                 ', "command": "AddUser"' + \
                 ', "parameters": {"round_table": false}}'
        self.u = '#abc/'
        pass

    def tearDown(self):
        pass

    def test_filter0(self):
        res = json_meta_command('abc', self.s)
        self.assertEqual(res, None)

    def test_filter1(self):
        res = json_meta_command('abc', self.t)
        # print(res)
        target = {"recipient_client_id": "ai", "recipient": "aa", "sender_client_id": "bi",
                               "sender": "bb", "command": "AddUser", "parameters": {"round_table": False}}
        # print(target)
        self.assertEqual(res, target)

    def test_filter2(self):
        res = json_meta_command('abd', self.s)
        self.assertEqual(res, None)

    def test_filter3(self):
        res = json_meta_command('abd', self.t)
        self.assertEqual(res, None)

    def test_filter4(self):
        res = json_meta_command('abc', self.u)
        self.assertEqual(res, None)

    def test_filter5(self):
        res = json_meta_command('abd', self.u)
        self.assertEqual(res, None)

if __name__ == '__main__':
    unittest.main()
