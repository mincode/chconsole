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
