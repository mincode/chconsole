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
def _dump_json_command(command, sender_client_id, sender, recipient_client_id, recipient, round_table, last_client,
                       round_restriction):
    """
    Dump json command as text.
    :param command: text representing the command.
    :param sender_client_id: client id of the sender user
    :param sender: sender name
    :param recipient_client_id: id of the recipient client or '' for all
    :param recipient: recipient name or '' for all
    :param round_table: True iff the sender thinks it is the round table moderator at sending.
    :param last_client: Ture, False None: True iff sender client is the last client of the sender user.
    :return: text version of the json-encoded command.
    """
    content = {'user': command, 'round_table': round_table}
    if last_client is not None:
        content['last_client'] = last_client

    json_text = json.dumps({'sender_client_id': sender_client_id, 'sender': sender,
                            'recipient_client_id': recipient_client_id, 'recipient': recipient,
                            'type': 'command', 'content': content})
    return json_text


def _command_source(session, json_dumped_command):
    """
    Provide the Python command source encapsulating a meta command encoded as json.
    :param session: session id.
    :param json_dumped_command: text version of the json-encoded command.
    :return:
    """
    return Source('#' + session + '/' + json_dumped_command, hidden=False)


class UserMessage(Code):
    chat_secret = ''  # secret identifying meta commands
    sender_client_id = ''  # client id of the sender user
    sender = ''  # sender name
    recipient_client_id = ''  # id of the recipient client or '' for all
    recipient = ''  # recipient name or '' for all
    round_table = False  # True iff the sender thinks it is the round table moderator at sending
    last_client = None  # True iff sender client is the last client of the sender user

    def __init__(self, command, chat_secret, sender_client_id, sender, recipient_client_id, recipient,
                 round_table, last_client):
        """
        Initialize.
        :param command: command text.
        :param chat_secret: secret identifying meta commands.
        :param sender_client_id: id of the client of the user.
        :param sender: name of the sender user.
        :param recipient_client_id: id of the recipient client; all if ''
        :param recipient: name of the recipient user; all if ''
        :param round_table True iff the sender thinks it is the round table moderator at sending.
        :param last_client: True iff client is the last client of the leanving user.
        """
        super(UserMessage, self).__init__(_command_source(chat_secret,
                                                          _dump_json_command(command, sender_client_id, sender,
                                                                             recipient_client_id, recipient,
                                                                             round_table, last_client)))
        self.chat_secret = chat_secret
        self.sender_client_id = sender_client_id
        self.sender = sender
        self.recipient_client_id = recipient_client_id
        self.recipient = recipient
        self.round_table = round_table
        self.last_client = last_client


class AddUser(UserMessage):
    """
    Message object indicating that the sender user is added to the system.
    """

    def __init__(self, chat_secret, sender_client_id, sender, recipient_client_id='', recipient='',
                 round_table=False):
        """
        Initialize.
        :param chat_secret: secret identifying meta commands.
        :param sender_client_id: id of the client of the sender user.
        :param sender: name of the sender user.
        :param recipient_client_id: id of the recipient's client; all if ''
        :param recipient: name of the recipient user; all if ''
        :param round_table True iff the sender thinks it is the round table moderator at sending.
        """
        super(AddUser, self).__init__('join', chat_secret, sender_client_id, sender, recipient_client_id, recipient,
                                      round_table, last_client=None)


class DropUser(UserMessage):
    """
    Message object indicating that the sender user is leaving.
    """
    def __init__(self, chat_secret, sender_client_id, sender, recipient_client_id='', recipient='',
                 round_table=False, last_client=True):
        """
        Initialize.
        :param chat_secret: secrets identifying meta commands.
        :param sender_client_id: id of the client of the user.
        :param sender: name of the sender user.
        :param recipient_client_id: id of the recipient's client; all if ''
        :param recipient: name of the recipient user; all if ''
        :param round_table True iff the sender thinks it is the round table moderator at sending.
        :param last_client: True iff client is the last client of the leanving user.
        """
        super(DropUser, self).__init__('leave', chat_secret, sender_client_id, sender, recipient_client_id,
                                       recipient, round_table, last_client)


class StopRoundTable(UserMessage):
    """
    Message object indicating that the sender stops its round table.
    """
    def __init__(self, chat_secret, sender_client_id, sender, recipient_client_id='', recipient=''):
        """
        Initialize.
        :param chat_secret: secrets identifying meta commands.
        :param sender_client_id: id of the client of the user.
        :param sender: name of the sender user.
        :param recipient_client_id: id of the recipient's client; all if ''
        :param recipient: name of the recipient user; all if ''
        """
        super(StopRoundTable, self).__init__('stop_round_table', chat_secret, sender_client_id, sender,
                                             recipient_client_id, recipient, round_table=True)


class StartRoundTable(UserMessage):
    """
    Message object indicating that the sender starts a round table.
    """
    def __init__(self, chat_secret, sender_client_id, sender, recipient_client_id='', recipient='',
                 round_restriction=1):
        """
        Initialize.
        :param chat_secret: secrets identifying meta commands.
        :param sender_client_id: id of the client of the user.
        :param sender: name of the sender user.
        :param recipient_client_id: id of the recipient's client; all if ''
        :param recipient: name of the recipient user; all if ''
        :param round_restriction: the number of responses each round table participant is allowed.
        """
        super(StartRoundTable, self).__init__('stop_round_table', chat_secret, sender_client_id, sender,
                                             recipient_client_id, recipient, round_table=True, last_client=False,
                                             round_restriction=round_restriction)


