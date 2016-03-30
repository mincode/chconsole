import json, os
from chconsole.configure import chconsole_data_dir

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Storage:
    name = ''  # file name of storage file
    data = None  # data dict

    def __init__(self, path, name):
        """
        Initizlize.
        :param name: file name, json file
        """
        os.makedirs(path, exist_ok=True)
        self.name = os.path.join(path, name)
        try:
            with open(self.name) as data_file:
                self.data = json.load(data_file)
        except FileNotFoundError:
            self.data = dict()
            self._dump()

    def _dump(self):
        """
        Dump data into storage file.
        """
        with open(self.name, 'w') as out_file:
            json.dump(self.data, out_file)

    def get(self, item):
        """
        Get stored item.
        :param item: name, string, of item to get.
        :return: stored item; raises a KeyError if item does not exist.
        """
        return self.data[item]

    def set(self, item, value):
        """
        Set item's value; causes the data to be dumped into the storage file.
        :param item: name, string of item to set.
        :param value: value to set.
        """
        self.data[item] = value
        self._dump()


class Persistent:
    """
    Item for storing in some persistent storage.
    """
    _storage = None  # Storage
    _name = ''

    def __init__(self, storage, name, value=None):
        """
        Initialize.
        :param storage: Storage.
        :param name: name, string, of item to store.
        :param value: value of the item.
        """
        self._storage = storage
        self._name = name
        self._storage.set(self._name, value)

    def get(self):
        """
        Get stored item.
        :return: stored item
        """
        return self._storage.get(self._name)

    def set(self, value):
        """
        Set item's value; causes the data to be dumped into the storage file.
        :param value: value to set.
        """
        self._storage.set(self._name, value)

s = Storage(chconsole_data_dir(), 'pers.json')
a = Persistent(s, 'a')
print('after constructor')
print('data: {}'.format(a.get()))
a.set(True)
print('data: {}'.format(a.get()))
