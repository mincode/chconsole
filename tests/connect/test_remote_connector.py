import unittest
from chconsole.connect.curie import Curie
from chconsole.connect.remote_connector import RemoteConnector
from chconsole.storage import chconsole_data_dir

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Tester(unittest.TestCase):
    def setUp(self):
        self.c0 = Curie('in.chgate.net/ijr7zolg')
        self.r0 = RemoteConnector(self.c0)
        pass

    def tearDown(self):
        pass

    def test_0(self):
        print(self.r0.info)
        print(chconsole_data_dir())
        res = True
        self.assertEqual(res, True)



if __name__ == '__main__':
    unittest.main()
