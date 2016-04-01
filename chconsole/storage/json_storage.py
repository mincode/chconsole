import os, json

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class JSONStorage:
    """
    File storage for a dictionary.
    """
    name = ''  # file name of storage file
    data = None  # data dict

    def __init__(self, path, name):
        """
        Initizlize.
        :param path: path to the storage file; empty means the current direcory.
        :param name: file name, json file
        """
        if path:
            os.makedirs(path, exist_ok=True)
        self.name = os.path.join(path, name)
        try:
            with open(self.name) as data_file:
                self.data = json.load(data_file)
        except FileNotFoundError:
            self.data = dict()
            self.dump()

    def dump(self):
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
        self.dump()
