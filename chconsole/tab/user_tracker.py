__author__ = 'Manfred Minimair <manfred@minimair.org>'


class UserTracker:
    _users = None  # list

    def __init__(self):
        """
        Initialize empty list.
        """
        self._users = list()

    @property
    def users(self):
        """
        List of users.
        :return: list of users.
        """
        return self._users

    def insert(self, user, unique_id):
        """
        Add user alphabethically.
        :param user: string of user name.
        :return: 
        """
        i = 0
        length = len(self._users)
        while i < length and user > self._users[i]:
            i += 1
        if length == 0 or (i != length and user != self._users[i]) or i == length:
            self._users.insert(i, user)

    def remove(self, user, unique_id):
        """
        Remove user from the list; no error if no such item.
        :param user: 
        :return: 
        """
        try:
            self._users.remove(user)
        except ValueError:
            pass
