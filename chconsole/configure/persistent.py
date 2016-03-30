__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Persistent:
    """
    Item for storing in some persistent storage.
    """
    _storage = None  # Storage
    _item = ''  # name of item whose value will be stored

    def __init__(self, storage, item, default_value=None):
        """
        Initialize.
        :param storage: Storage.
        :param item: name, string, of item to store.
        :param default_value: default value of the item; only used if the item is not yet in the storage.
        """
        self._storage = storage
        self._item = item
        try:
            self._storage.get(self._item)
        except KeyError:
            self._storage.set(self._item, default_value)

    def get(self):
        """
        Get stored item.
        :return: stored item
        """
        return self._storage.get(self._item)

    def set(self, value):
        """
        Set item's value; causes the data to be dumped into the storage file.
        :param value: value to set.
        """
        self._storage.set(self._item, value)
