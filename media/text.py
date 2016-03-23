import sys
import re
from unicodedata import category
from qtconsole.qt import QtGui
from .line_iter import LineIter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


# JupyterWidget
if sys.platform.startswith('win'):
    default_editor = 'notepad'
else:
    default_editor = ''


# ConsoleWidget
def get_block_plain_text(block):
    """ Given a QTextBlock, return its unformatted text.
    """
    cursor = QtGui.QTextCursor(block)
    cursor.movePosition(QtGui.QTextCursor.StartOfBlock)
    cursor.movePosition(QtGui.QTextCursor.EndOfBlock,
                        QtGui.QTextCursor.KeepAnchor)
    return cursor.selection().toPlainText()


# ConsoleWdidget
def is_letter_or_number(char):
    """ Returns whether the specified unicode character is a letter or a number.
    """
    cat = category(char)
    return cat.startswith('L') or cat.startswith('N')


# ConsoleWidget
def set_top_cursor(receiver, cursor):
    """ Scrolls the viewport so that the specified cursor is at the top.
    """
    scrollbar = receiver.verticalScrollBar()
    scrollbar.setValue(scrollbar.maximum())
    original_cursor = receiver.textCursor()
    receiver.setTextCursor(cursor)
    receiver.ensureCursorVisible()
    receiver.setTextCursor(original_cursor)


def double_backslash(s):
    """
    Escape backslashes to work with regex.
    :param s: string.
    :return: string where backslashes are replaced with double backslash.
    """
    return re.sub(r'\\', r'\\\\', s)


def starts_with(s, init='#'):
    """
    Check whether a string starts with whitespaces followed by pound sign.
    :param s: string to be checked.
    :param init: initial chars denoting a line comment.
    :return: whether the string starts with whitespaces followed by pound sign.
    """
    return True if re.match('^\s*' + double_backslash(init), s) else False


def is_comment(s, init='#'):
    """
    Determine whether the string represents a (multi-line) comment, accepting empty lines as well.
    :param s: string to be checked.
    :param init: initial chars denoting a line comment.
    :return: True if all the lines in the string start with whitespace followed by the pound sign.
    """
    lines = LineIter(s)
    for i in lines:
        if not(starts_with(i, init) or i == ''):
            return False
    return True


def to_comment(s, init='#'):
    """
    Convert string into a string with a (multi-line) comment.
    :param init: initial chars denoting a line comment.
    :param s: string to be converted.
    :return: the string with pound signs prepended to each line.
    """
    return re.sub('^', init, s, flags=re.MULTILINE)


def de_comment(s, init='#', end='\\'):
    """
    Turn a string of line comments into a string without the comment markers.
    :param s:
    :param init: string of initial chars denoting a line comment.
    :param end: string of chars optionally terminating a line comment.
    :return: s where initial and terminating chars are removed, however, initial chars are only removed when
     preceded by whitespaces.
    """
    end_escaped = double_backslash(end)
    lines = LineIter(s)
    stripped = list()
    for i in lines:
        de = i
        if starts_with(de, init):
            match = re.search(init, de)
            de = de[:match.start()] + de[match.end():]
        de = re.sub(end_escaped + '$', '', de)
        stripped.append(de)
    return '\n'.join(stripped)
