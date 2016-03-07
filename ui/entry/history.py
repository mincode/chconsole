from ipython_genutils.py3compat import unicode_type
from qtconsole.qt import QtGui
from .history_filter import HistoryFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class History:
    _target = None  # target Q(Plain)TextEdit editor where history is recorded

    _items = None  # list of history items
    _edits = None  # dict (index, str) of edited history items
    _index = 0  # index of current history item
    _prefix = ''  # string used as prefix to only show history items with this prefix

    _filter = None  # HistoryFilter

    def __init__(self, target):
        self._target = target
        self._items = []
        self._edits = {}
        self._filter = HistoryFilter(self._target)
        self._target.installEventFilter(self._filter)

    # HistoryConsoleWidget
    def _get_edited_item(self, index):
        """ Retrieves a history item, possibly with temporary edits.
        """
        if index in self._edits:
            return self._edits[index]
        elif index == len(self._items):
            return unicode_type()
        return self._items[index]

    # HistoryConsoleWidget
    def _store_edits(self):
        """ If there are edits to the current input buffer, store them.
        """
        current = self._target.toPlainText()
        if self._index == len(self._items) or self._items[self._index] != current:
            self._edits[self._index] = current

    # HistoryConsoleWidget
    def store(self, source):
        # Save the command unless it was an empty string or was identical
        # to the previous command.
        if not source.hidden:
            item = source.code.rstrip()
            if item and (not self._items or self._items[-1] != item):
                self._items.append(item)

            # Reset all history edits.
            self._edits = {}

            # Move the history index to the most recent item.
            self._index = len(self._items)

    # HistoryConsoleWidget
    def previous(self, substring='', as_prefix=True):
        """ If possible, set the input buffer to a previous history item.

        Parameters
        ----------
        substring : str, optional
            If specified, search for an item with this substring.
        as_prefix : bool, optional
            If True, the substring must match at the beginning (default).

        Returns
        -------
        Whether the input buffer was changed.
        """
        replace = False
        index = self._index
        while index > 0:
            index -= 1
            history = self._get_edited_item(index)
            if (as_prefix and history.startswith(substring)) or (not as_prefix and substring in history):
                self._store_edits()
                self._index = index
                self._target.document().setPlainText(history)
                replace = True
                break

        return replace

    # HistoryConsoleWidget
    def next(self, substring='', as_prefix=True):
        """ If possible, set the input buffer to a subsequent history item.

        Parameters
        ----------
        substring : str, optional
            If specified, search for an item with this substring.
        as_prefix : bool, optional
            If True, the substring must match at the beginning (default).

        Returns
        -------
        Whether the input buffer was changed.
        """
        replace = False
        index = self._index
        while index < len(self._items):
            index += 1
            history = self._get_edited_item(index)
            if (as_prefix and history.startswith(substring)) or (not as_prefix and substring in history):
                self._store_edits()
                self._index = index
                self._target.document().setPlainText(history)
                replace = True
                break

        return replace

    def key_up(self, shift_down):
        """
        History on up key.
        :param shift_down:
        :return:
        """
        # Set a search prefix based on the cursor position.
        cursor = self._target.textCursor()
        col = cursor.columnNumber()
        input_buffer = self._target.toPlainText()
        # use the *shortest* of the cursor column and the history prefix
        # to determine if the prefix has changed
        n = min(col, len(self._prefix))

        # prefix changed, restart search from the beginning
        if self._prefix[:n] != input_buffer[:n]:
            self._index = len(self._items)

        # the only time we shouldn't set the history prefix
        # to the line up to the cursor is if we are already
        # in a simple scroll (no prefix),
        # and the cursor is at the end of the first line

        # check if we are at the end of the first line
        current_pos = cursor.position()
        cursor.movePosition(QtGui.QTextCursor.EndOfLine)
        at_eol = (cursor.position() == current_pos)

        if self._index == len(self._items) or not (self._prefix == '' and at_eol) or \
                not (self._get_edited_item(self._index)[:col] == input_buffer[:col]):
            self._prefix = input_buffer[:col]

        # Perform the search.
        self.previous(self._prefix, as_prefix=not shift_down)

        # Go to the first line of the prompt for seemless history scrolling.
        # Emulate readline: keep the cursor position fixed for a prefix
        # search.
        cursor.movePosition(QtGui.QTextCursor.Start)
        if self._prefix:
            cursor.movePosition(QtGui.QTextCursor.Right,
                                n=len(self._prefix))
        else:
            cursor.movePosition(QtGui.QTextCursor.EndOfLine)
        self._target.setTextCursor(cursor)

    # HistoryConsoleWidget
    def key_down(self, shift_down):
        """
        History on down key.
        :param shift_down:
        :return:
        """
        # Perform the search.
        replaced = self.next(self._prefix, as_prefix=not shift_down)

        # Emulate readline: keep the cursor position fixed for a prefix
        # search. (We don't need to move the cursor to the end of the buffer
        # in the other case because this happens automatically when the
        # input buffer is set.)
        if self._prefix and replaced:
            cursor = self._target.textCursor()
            cursor.movePosition(QtGui.QTextCursor.Start)
            cursor.movePosition(QtGui.QTextCursor.Right,
                                n=len(self._prefix))
            self._target.setTextCursor(cursor)
