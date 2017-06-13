import json
from chconsole.messages import UserJoin, UserLeave


__author__ = 'Manfred Minimair <manfred@minimair.org>'


def filter_meta(session, code):
    """
    Determine if code represents a meta instruction for the chat system of the
    form: whitespaces #session_id/json-string
    :param session: session id.
    :param code: code sent through the system.
    :return: dict representing the meta instruction or None if none; session parameter must match session_id in code.
    """
    stripped = code.lstrip()
    instruction = None
    if stripped[0] == '#':
        session_end = len(session) + 1
        if stripped[1:session_end] == session:
            if stripped[session_end] == '/':
                rest = stripped[session_end+1:]
                try:
                    instruction = json.loads(rest)
                except json.JSONDecodeError:
                    pass
    return instruction


def is_command_meta(chat_instruction):
    """
    Determine whether chat_instructions represents a correct meta command.
    :param chat_instruction: dict or None
    :return: True if chat_instruction represents a correct meta command.
    """

    return isinstance(chat_instruction, dict) \
           and chat_instruction.get('type', '') == 'command' and chat_instruction.get('content', None) != None


def is_chat_meta(chat_instruction):
    """
    Determine whether chat_instructions represents a correct chat message.
    :param chat_instruction: dict or None
    :return: True if chat_instruction represents a correct chat message
    """
    return isinstance(chat_instruction, dict) and \
           chat_instruction.get('type', '') == 'chat' and chat_instruction.get('content', None) != None


def is_user_command(chat_instruction):
    """
    Determine whether chat_instruction represents a correct user command.
    :param chat_instruction: dict which is a meta command
    :return: True if chat_instruction represents a correct user command.
    """

    user = chat_instruction['content'].get('user', '')
    if user == 'join':
        res = True
    elif user == 'leave':
        res = True
    else:
        res = False
    return res


def process_command_meta(chat_instruction, username):
    """
    Create importable object for the command.
    :param chat_instruction: meta command dict.
    :param user name of the user who has received the chat_instruction in the current client.
    :return: Importable object.
    """
    meta = None
    if is_user_command(chat_instruction):
        client_id = chat_instruction['client_id']
        sender = chat_instruction['sender']
        if chat_instruction['content']['user'] == 'join':
            meta = UserJoin(sender, client_id)
        elif chat_instruction['content']['user'] == 'who':
                meta = UserName(username, client_id, sender)
        elif chat_instruction['content']['user'] == 'leave':
            meta = UserLeave(sender, client_id)
    return meta

