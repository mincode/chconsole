from qtconsole.qt import QtGui
__author__ = 'Manfred Minimair <manfred@minimair.org>'


class CenteredText:
    """
    Text that is centered in  a field that can be removed and shown.
    """
    _pos = None  # start cursor position of text
    _text = ''  # text to be inserted

    def __init__(self, start=0, text=''):
        self._pos = start
        self._text = text

    def insert(self, target, field):
        """
        Show the text.
        :param target: QTextDocument where to show the text.
        :param field: length of the field to center text; if the text is longer than field, only the
        initial fitting chars of text are used.
        :return:
        """
        text = self._text if len(self._text) <= field else self._text[:field]
        cursor = QtGui.QTextCursor(target)
        cursor.setPosition(self._pos)
        cursor.insertText('{{:^{}}}'.format(field).format(text))

    def remove(self, target, field):
        """
        Remove text of a given length.
        :param target: QTextDocument where to remove the text.
        :param field: length of the field to remove.
        :return:
        """
        cursor = QtGui.QTextCursor(target)
        cursor.setPosition(self._pos)
        cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, field)
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

    def center(self, target, field, new_field):
        """
        Center text in a new field.
        :param target: QTextDocument target.
        :param field: existing field length within which text has been centered.
        :param new_field: new field length >= field.
        :return:
        """
        text_len = len(self._text)
        spaces = field - text_len
        left = spaces // 2
        right = left
        right_extra = (spaces - left - right) != 0
        # whether there is one more space to the right than to the left of the text

        new_spaces = new_field - field
        new_left = new_spaces//2
        new_right = new_left
        new_extra = (new_spaces - new_left - new_right) != 0
        # whether there is one extra space to be inserted to the left or to the right

        cursor = QtGui.QTextCursor(target)
        cursor.setPosition(self._pos)
        if new_left > 0:
            cursor.insertText(' '*new_left)
        if right_extra and new_extra:
            cursor.insertText(' ')
        if left+text_len > 0:
            cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor, left+text_len)
        if new_right > 0:
            cursor.insertText(' '*new_right)
        if (not right_extra) and new_extra:
            cursor.insertText(' ')
