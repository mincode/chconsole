from .user_client import UserClient


__author__ = 'Manfred Minimair <manfred@minimair.org>'


class UserTracker:
    """
    Sorted list of users in ascending order.
    """
    _users = None  # list of UserClient

    def __init__(self):
        """
        Initialize empty list.
        """
        self._users = list()

    @property
    def users(self):
        """
        List of users.
        :return: list of users and client ids.
        """
        return self._users

    @property
    def names(self):
        """
        List of user names.
        :return: list of user names.
        """
        names_list = [user.name for user in self._users]
        return names_list

    def insert(self, user, client_id):
        """
        Add user alphabethically.
        :param user: string of user name.
        :param client_id: string of unique client id of user.
        :return: 
        """
        i = 0
        length = len(self._users)
        while i < length and user > self._users[i].name:
            i += 1
        if length == 0 or (i != length and user != self._users[i].name) or i == length:
            self._users.insert(i, UserClient(user, [client_id]))
        elif user == self._users[i].name and client_id not in self._users[i].clients:
            self._users[i].clients.append(client_id)

    def remove(self, user, client_id):
        """
        Remove user from the list; no error if no such item.
        :param user: string of user name
        :param client_id: string of unique client id of user.
        :return: 
        """
        length = len(self._users)
        for i in range(0, length):
            user_client = self._users[i]
            if user == user_client.name:
                try:
                    user_client.clients.remove(client_id)
                except ValueError:
                    pass
                if not user_client.clients:
                    del self._users[i]
                break

    def find_user(self, user_name):
        """
        Find user.
        :param user_name: name of the user.
        :return: UserClient object of the user if found; None otherwise.
        """
        found = None
        for user_client in self._users:
            if user_name == user_client.name:
                found = user_client
                break
        return found

    def last_client(self, user_name):
        """
        Determine whether this is the user's last client.
        :param user_name: name of the user
        :return: True iff this is the only client of the current user.
        """
        connected = self.find_user(user_name)
        answer = False
        if connected and len(connected.clients) > 0:
            answer = len(connected.clients) == 1
        return answer

    def html_user_list(self, user_name):
        """
        List all users connected to the tab.
        :param user_name: name of the current user.
        :return: html text listing all users; current user indicated with (me); empty string if no users.
        """
        names = self.names
        num = len(names)
        if num > 0:
            out_text = 'Connected Users<hr><br>'
            out_text = out_text + names[0]
            if names[0] == user_name:
                out_text = out_text + ' (me)'
            # print(out_text)
            for i in range(1, num):
                out_text = out_text + '<br>' + names[i]
                if names[i] == user_name:
                    out_text = out_text + ' (me)'
        else:
            out_text = ''
        return out_text
