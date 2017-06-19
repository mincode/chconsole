__author__ = 'Manfred Minimair <manfred@minimair.org>'


class UserClient:
    """
    Stores the user name and list of client ids used by the user.
    """
    name = ''  # user name
    clients = None  # list of client ids

    def __init__(self, name='', clients=list()):
        self.name = name
        self.clients = clients

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

