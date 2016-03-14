from unicodedata import category
from qtconsole.qt import QtGui

__author__ = 'Manfred Minimair <manfred@minimair.org>'


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
