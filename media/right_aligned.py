from qtconsole.qt import QtGui
__author__ = 'Manfred Minimair <manfred@minimair.org>'


class RightAligned:
    """
    Text that is right-aligned in  a field that can be removed and shown.
    """
    _pos = None  # start cursor position of text
    _text = None  # text to be inserted, or None
    _right_end = '> '  # right terminator of the text when shown

    def __init__(self, start=0, text=None, right_end='> '):
        self._pos = start
        self._text = text
        self._right_end = right_end

    @property
    def right_length(self):
        """
        The length of right terminator.
        :return:
        """
        return len(self._right_end)

    def insert(self, target, field):
        """
        Show the text; or blanks instead of text and the right terminator if the text is None.
        :param target: QTextDocument where to show the text.
        :param field: length of the field for the text; if the text is longer than field, only the
        initial fitting chars of text are used.
        :return:
        """
        cursor = QtGui.QTextCursor(target)
        cursor.setPosition(self._pos)
        if self._text is None:
            cursor.insertText(' '*(field + self.right_length))
        else:
            text = self._text if len(self._text) <= field else self._text[:field]
            cursor.insertText('{{:>{}}}'.format(field).format(text) + self._right_end)

    def remove(self, target, field):
        """
        Remove text of a given length, as well as the right terminator.
        :param target: QTextDocument where to remove the text.
        :param field: length of the field to remove.
        :return:
        """
        cursor = QtGui.QTextCursor(target)
        cursor.setPosition(self._pos)
        cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, field + len(self._right_end))
        cursor.deleteChar()

    def shift(self, offset):
        """
        Shift the position of the text field.
        :param offset: int by which to shift the position of the text field (can be negative for left shift down to 0).
        :return: new position.
        """
        new_pos = self._pos + offset
        self._pos = new_pos if new_pos >= 0 else 0
        return self._pos

    def adjust(self, target, field, new_field):
        """
        Right align text in a new field.
        :param target: QTextDocument target.
        :param field: existing field length within which text has been centered.
        :param new_field: new field length >= field.
        :return:
        """
        new_spaces = new_field - field
        if new_spaces > 0:
            cursor = QtGui.QTextCursor(target)
            cursor.setPosition(self._pos)
            cursor.insertText(' '*new_spaces)
