import json
from .source import Source

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class ExportItem:
    pass


class Interrupt(ExportItem):
    pass


class Exit(ExportItem):
    keep_kernel = True  # whether to keep the kernel on exit

    def __init__(self, keep_kernel=True):
        super(Exit, self).__init__()
        self.keep_kernel = keep_kernel


class Restart(ExportItem):
    clear = True  # whether to clear on restart

    def __init__(self, clear=True):
        super(Restart, self).__init__()
        self.clear = clear


class UserInput(ExportItem):
    """
    User input given to an input request from the kernel.
    """
    text = ''  # user input as text

    def __init__(self, text=''):
        super(UserInput, self).__init__()
        self.text = text


class TailHistory(ExportItem):
    """
    Tail history request.
    """
    length = 1000  # last length history items

    def __init__(self, length=1000):
        super(TailHistory, self).__init__()
        self.length = length


class Code(ExportItem):
    source = None  # Source

    def __init__(self, source):
        super(Code, self).__init__()
        self.source = source


class Execute(Code):
    pass


class CodeFragment(Code):
    position = 0  # int

    def __init__(self, source, position):
        super(CodeFragment, self).__init__(source)
        self.position = position


class Inspect(CodeFragment):
    pass


class Complete(CodeFragment):
    pass


# User Management

class UserMessage(Code):
    session = None  # session id; string
    client_id = None  # client id of the sender user; string
    sender = None  # sender name; string
    recipient = None  # recipient name or '' for all; string

    def __init__(self, source, session, client_id, sender, recipient=''):
        """
        Initialize.
        :param source: source code; Source
        :param session: session id.
        :param client_id: id of the client of the user.
        :param sender: name of the sender user.
        :param recipient: name of the recipient user; all if ''
        """
        super(UserMessage, self).__init__(source)
        self.session = session
        self.client_id = client_id
        self.sender = sender
        self.recipient = recipient


class AddUser(UserMessage):
    def __init__(self, session, client_id, sender, recipient_client_id='', recipient=''):
        """
        Initialize.
        :param session: session id. 
        :param client_id: id of the client of the sender user.
        :param sender: name of the sender user.
        :param recipient_client_id: id of the recipient's client; all if ''
        :param recipient: name of the recipient user; all if ''
        """
        command = json.dumps({'client_id': client_id, 'sender': sender,
                              'recipient_client_id': recipient_client_id, 'recipient': recipient,
                              'type': 'command', 'content': {'user': 'join'}})
        super(AddUser, self).__init__(Source(
            '#' + session + '/' + command, hidden=False), session, client_id, sender,
            recipient_client_id, recipient)


class WhoUser(UserMessage):
    def __init__(self, session, client_id, sender, recipient_client_id='', recipient=''):
        """
        Initialize.
        :param session: session id.
        :param client_id: id of the client of the user.
        :param sender: name of the sender user.
        :param recipient_client_id: id of the recipient's client; all if ''
        :param recipient: name of the recipient user; all if ''
        """
        command = json.dumps({'client_id': client_id, 'type': 'command', 'content': {'user': 'who'}})
        super(WhoUser, self).__init__(Source(
            '#' + session + '/' + command, hidden=False), session, client_id, sender,
            recipient_client_id, recipient)


class DropUser(UserMessage):
    def __init__(self, session, client_id, sender, recipient_client_id='', recipient=''):
        """
        Initialize.
        :param session: session id. 
        :param client_id: id of the client of the user.
        :param sender: name of the sender user.
        :param recipient_client_id: id of the recipient's client; all if ''
        :param recipient: name of the recipient user; all if ''
        """
        command = json.dumps({'client_id': client_id, 'type': 'command', 'content': {'user': 'leave'}})
        super(DropUser, self).__init__(Source(
            '#' + session + '/' + command, hidden=False), session, client_id, sender,
            recipient_client_id, recipient)
