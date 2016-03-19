from qtconsole.qt import QtGui
__author__ = 'Manfred Minimair <manfred@minimair.org>'


class FlexibleText:
    """
    Text that can be hidden and shown. Multiple FlexibleTest should be hidden in reverse order they are shown,
    and vice versa.
    """
    _target = None  # Q(Plain)TextEdit
    _text = ''  # text to be inserted
    _start = None  # start cursor of text
    _end = None  # end cursor of text
    _visible = False  # whether the text is visible

    def __init__(self, target, text='', cursor=None):
        self._target = target
        self._text = text
        self._start = cursor.position() if cursor else self._target.textCursor().position()
        self._text = text

    def show(self):
        """
        Show the text.
        :return:
        """
        if not self._visible:
            cursor = QtGui.QTextCursor(self._target.document())
            cursor.setPosition(self._start)
            cursor.insertText(self._text)
            self._end = cursor.position()
            self._visible = True

    def hide(self):
        """
        Hide the text.
        :return:
        """
        if self._visible:
            cursor = QtGui.QTextCursor(self._target.document())
            cursor.setPosition(self._start)
            cursor.setPosition(self._end, QtGui.QTextCursor.KeepAnchor)
            cursor.deleteChar()
            self._end = cursor.position()
            self._visible = False
