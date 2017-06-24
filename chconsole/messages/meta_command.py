import json
from .export_item import ExportItem
from .import_item import ImportItem
from .source import Source

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class MetaCommand(ExportItem, ImportItem):
    """
    Meta command sent through chat.
    Format:
    #chat_secret/meta_command

    meta_command format: json of a dict:
    {'sender_client_id': sender_client_id, 'sender': sender,
    'recipient_client_id': recipient_client_id, 'recipient': recipient,
    'command': {'AddUser:, 'DropUser', 'NewRoundTable', 'StopRoundTable'},
    'parameters': parameters}

    AddUser: command == AddUser
    {'round_table': {True, False}, 'restriction': Int}

    DropUser: command == DropUser
    {'round_table': {True, False}, 'last_client': {True, False}}

    StopRoundTable: command == StopRoundTable
    sender claims not to be the moderator of the round table anymore
    {}

    NewRoundTable: command == StartRoundTable
    sender starts a new round table; sends number of communications allowed
    {'restriction': Int}
    """
    chat_secret = ''  # secret identifying meta commands
    sender_client_id = ''  # client id of the sender user
    sender = ''  # sender name
    recipient_client_id = ''  # id of the recipient client or '' for all
    recipient = ''  # recipient name or '' for all
    parameters = None  # dict of paramters of the command

    def __init__(self, chat_secret='', sender_client_id='', sender='', recipient_client_id='', recipient=''):
        """
        Initialize.
        :param chat_secret: secret identifying meta commands.
        :param sender_client_id: id of the client of the user.
        :param sender: name of the sender user.
        :param recipient_client_id: id of the recipient client; all if ''
        :param recipient: name of the recipient user; all if ''
        """
        ImportItem.__init__(self, username=sender)
        ExportItem.__init__(self)
        self.chat_secret = chat_secret
        self.sender_client_id = sender_client_id
        self.sender = sender
        self.recipient_client_id = recipient_client_id
        self.recipient = recipient
        self.parameters = dict()

    @property
    def _command_dict(self):
        """
        Dict representing the command.
        :return: dict representing the command.
        """
        command_dict = dict()
        command_dict['sender_client_id'] = self.sender_client_id
        command_dict['sender'] = self.sender
        command_dict['recipient_client_id'] = self.recipient_client_id
        command_dict['recipient'] = self.recipient
        command_dict['command'] = self.type
        command_dict['parameters'] = self.parameters
        return command_dict

    @property
    def _command_json(self):
        """
        json representing the command.
        :return: json representing the command.
        """
        # print('ABOUT TO JSON DUMP: ', self._command_dict)
        return json.dumps(self._command_dict)

    @property
    def _code(self):
        """
        comment text representing the command.
        :return: comment text representing the command.
        """
        return '#' + self.chat_secret + '/' + self._command_json

    @property
    def source(self):
        """
        Command Source.
        :return: command Source.
        """
        return Source(self._code, hidden=False)

    def to_all_clients(self):
        """
        Determine if the message is going to all clients
        :return: True if the message goes to all clients.
        """
        return self.recipient_client_id == ''

    def to(self, client_id, user_name):
        """
        Determine if the message is going to client_id and user_name
        :param client_id: id of current client.
        :param user_name: user name.
        :return: True if the message goes to client_id and user_name.
        """
        match = False
        if self.recipient_client_id == '':
            if self.recipient == '':
                match = True
            elif self.recipient == user_name:
                match = True
        elif self.recipient_client_id == client_id:
            if self.recipient == user_name:
                match = True
        return match


class AddUser(MetaCommand):
    """
    Message object indicating that the sender user is added to the system.
    """

    def __init__(self, chat_secret, sender_client_id, sender, recipient_client_id='', recipient='',
                 round_table=False, restriction=-1):
        """
        Initialize.
        :param chat_secret: secret identifying meta commands.
        :param sender_client_id: id of the client of the sender user.
        :param sender: name of the sender user.
        :param recipient_client_id: id of the recipient's client; all if ''
        :param recipient: name of the recipient user; all if ''
        :param round_table True iff the sender thinks it is the round table moderator at sending.
        :param restriction: the number of responses each round table participant is allowed.
        """
        super(AddUser, self).__init__(chat_secret, sender_client_id, sender, recipient_client_id, recipient)
        self.parameters = {'round_table': round_table, 'restriction': restriction}


class DropUser(MetaCommand):
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
        super(DropUser, self).__init__(chat_secret, sender_client_id, sender, recipient_client_id, recipient)
        self.parameters = {'round_table': round_table, 'last_client': last_client}


class StopRoundTable(MetaCommand):
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
        super(StopRoundTable, self).__init__(chat_secret, sender_client_id, sender, recipient_client_id, recipient)


class StartRoundTable(MetaCommand):
    """
    Message object indicating that the sender starts a round table.
    """
    def __init__(self, chat_secret, sender_client_id, sender, recipient_client_id='', recipient='',
                 restriction=1):
        """
        Initialize.
        :param chat_secret: secrets identifying meta commands.
        :param sender_client_id: id of the client of the user.
        :param sender: name of the sender user.
        :param recipient_client_id: id of the recipient's client; all if ''
        :param recipient: name of the recipient user; all if ''
        :param restriction: the number of responses each round table participant is allowed.
        """
        super(StartRoundTable, self).__init__(chat_secret,
                                              sender_client_id, sender, recipient_client_id, recipient)
        self.parameters = {'restriction': restriction}


def _get_meta_command(chat_secret, instruction):
    """
    Create importable MetaCommand object for the command.
    :param chat_secret: chat secret of system.
    :param instruction: meta command dict.
    :return: Importable object; or None if nothing to be done.
    """
    meta = None
    sender_client_id = instruction['sender_client_id']
    sender = instruction['sender']
    recipient = instruction['recipient']
    recipient_client_id = instruction['recipient_client_id']
    command = instruction['command']
    parameters = instruction['parameters']
    if command == 'AddUser':
        round_table = parameters['round_table']
        restriction = parameters['restriction']
        meta = AddUser(chat_secret, sender_client_id, sender, recipient_client_id, recipient,
                       round_table, restriction)
    elif command == 'DropUser':
        round_table = parameters['round_table']
        last_client = parameters['last_client']
        meta = DropUser(chat_secret, sender_client_id, sender, recipient_client_id, recipient,
                        round_table, last_client)
    elif command == 'StopRoundTable':
        meta = StopRoundTable(chat_secret, sender_client_id, sender, recipient_client_id, recipient)
    elif command == 'StartRoundTable':
        restriction = parameters['restriction']
        meta = StartRoundTable(chat_secret, sender_client_id, sender, recipient_client_id, recipient, restriction)

    return meta


def json_meta_command(chat_secret, code):
    """
    Determine if code represents a meta instruction for the chat system of the
    form: whitespaces #chat_secret/json-string
    :param chat_secret: secret string identifying session.
    :param code: code sent through the system.
    :return: json representing the meta instruction or None if none;
    session parameter must match session_id in code.
    """
    stripped = code.lstrip()
    instruction = None
    if stripped[0] == '#':
        session_end = len(chat_secret) + 1
        if stripped[1:session_end] == chat_secret:
            if stripped[session_end] == '/':
                rest = stripped[session_end+1:]
                try:
                    instruction = json.loads(rest)
                except json.JSONDecodeError:
                    pass
                if not isinstance(instruction, dict):
                    instruction = None
                elif 'sender_client_id' not in instruction:
                    instruction = None
                elif 'sender' not in instruction:
                    instruction = None
                elif 'recipient_client_id' not in instruction:
                    instruction = None
                elif 'recipient' not in instruction:
                    instruction = None
                elif 'command' not in instruction:
                    instruction = None
                elif 'parameters' not in instruction:
                    instruction = None
    return instruction


def filter_meta_command(chat_secret, code):
    """
    Determine if code represents a meta instruction for the chat system of the
    form: whitespaces #chat_secret/json-string
    :param chat_secret: secret string identifying session.
    :param code: code sent through the system.
    :return: dict representing the meta instruction or None if none; session parameter must match session_id in code.
    """
    instruction = json_meta_command(chat_secret, code)
    if instruction:
        meta_command = _get_meta_command(chat_secret, instruction)
    else:
        meta_command = None
    return meta_command
