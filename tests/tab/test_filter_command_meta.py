import unittest

from chconsole.messages import filter_meta_command
from chconsole.messages import AddUser, DropUser, StartRoundTable, StopRoundTable

__author__ = 'minimair'


class Tester(unittest.TestCase):
    def setUp(self):
        self.s = '#abc/{"recipient_client_id": "ai", "recipient": "aa"' + \
                 ', "sender_client_id": "bi", "sender": "bb"' + \
                 ', "command": "AddUser"' + \
                 ', "parameters": {"round_table": false}}'
        self.t = '#abc/{"recipient_client_id": "ai", "recipient": "aa"' + \
                 ', "sender_client_id": "bi", "sender": "bb"' + \
                 ', "command": "DropUser"' + \
                 ', "parameters": {"round_table": true, "last_client": true}}'
        self.u = '#abc/{"recipient_client_id": "ai", "recipient": "aa"' + \
                 ', "sender_client_id": "bi", "sender": "bb"' + \
                 ', "command": "StartRoundTable"' + \
                 ', "parameters": {"restriction": 3}}'
        self.v = '#abc/{"recipient_client_id": "ai", "recipient": "aa"' + \
                 ', "sender_client_id": "bi", "sender": "bb"' + \
                 ', "command": "StopRoundTable"' + \
                 ', "parameters": {}}'
        self.w = '#abc/{"recipient_client_id": "ai", "recipient": "aa"' + \
                 ', "sender_client_id": "bi", "sender": "bb"' + \
                 ', "command": "Wrong"' + \
                 ', "parameters": {}}'
        pass

    def tearDown(self):
        pass

    def test_filter0(self):
        processed = filter_meta_command('abc', self.s)
        # print('processed', processed.username)
        res = isinstance(processed, AddUser) and processed.sender == 'bb'
        # print('result', res)
        self.assertEqual(res, True)

    def test_filter1(self):
        processed = filter_meta_command('abc', self.t)
        res = isinstance(processed, DropUser) and processed.sender == 'bb'
        self.assertEqual(res, True)

    def test_filter2(self):
        processed = filter_meta_command('abc', self.w)
        res = processed == None
        self.assertEqual(res, True)

    def test_filter3(self):
        processed = filter_meta_command('abc', self.u)
        res = isinstance(processed, StartRoundTable) and processed.sender == 'bb'
        self.assertEqual(res, True)

    def test_filter4(self):
        processed = filter_meta_command('abc', self.v)
        res = isinstance(processed, StopRoundTable) and processed.sender == 'bb'
        self.assertEqual(res, True)


if __name__ == '__main__':
    unittest.main()
