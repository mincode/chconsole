from ipython_genutils.py3compat import unicode_type
from qtconsole.qt import QtGui
from .history_filter import HistoryFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class History:
    _target = None  # target Q(Plain)TextEdit editor where history is recorded

    _history = None  # list of history items
    _history_edits = None  # dict (index, str) of edited history items
    _history_index = 0  # index of current history item
    _history_prefix = ''  # string used as prefix to only show history items with this prefix

    _filter = None  # HistoryFilter

    def __init__(self, target):
        self._target = target
        self._history = []
        self._history_edits = {}
        self._filter = HistoryFilter(self._target)
        self._target.installEventFilter(self._filter)

    # HistoryConsoleWidget
    def _get_edited_history(self, index):
        """ Retrieves a history item, possibly with temporary edits.
        """
        if index in self._history_edits:
            return self._history_edits[index]
        elif index == len(self._history):
            return unicode_type()
        return self._history[index]

    # HistoryConsoleWidget
    def _store_edits(self):
        """ If there are edits to the current input buffer, store them.
        """
        current = self.target.toPlainText()
        if self._history_index == len(self._history) or \
                self._history[self._history_index] != current:
            self._history_edits[self._history_index] = current

    # HistoryConsoleWidget
    def store(self, source):
        # Save the command unless it was an empty string or was identical
        # to the previous command.
        if not source.hidden:
            item = source.code.rstrip()
            if item and (not self._history or self._history[-1] != item):
                self._history.append(item)

            # Reset all history edits.
            self._history_edits = {}

            # Move the history index to the most recent item.
            self._history_index = len(self._history)

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
        index = self._history_index
        replace = False
        while index > 0:
            index -= 1
            history = self._get_edited_history(index)
            if (as_prefix and history.startswith(substring)) \
                or (not as_prefix and substring in history):
                replace = True
                break

        if replace:
            self._store_edits()
            self._history_index = index
            self.target.document().setPlainText(history)

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
        index = self._history_index
        replace = False
        while index < len(self._history):
            index += 1
            history = self._get_edited_history(index)
            if (as_prefix and history.startswith(substring)) \
                or (not as_prefix and substring in history):
                replace = True
                break

        if replace:
            self._store_edits()
            self._history_index = index
            self.target.document().setPlainText(history)

        return replace

    def key_up(self, shift_down):
        """
        History on up key.
        :param shift_down:
        :return:
        """
        # Set a search prefix based on the cursor position.
        col = self._get_input_buffer_cursor_column()
        input_buffer = self.input_buffer
        # use the *shortest* of the cursor column and the history prefix
        # to determine if the prefix has changed
        n = min(col, len(self._history_prefix))

        # prefix changed, restart search from the beginning
        if (self._history_prefix[:n] != input_buffer[:n]):
            self._history_index = len(self._history)

        # the only time we shouldn't set the history prefix
        # to the line up to the cursor is if we are already
        # in a simple scroll (no prefix),
        # and the cursor is at the end of the first line

        # check if we are at the end of the first line
        c = self._get_cursor()
        current_pos = c.position()
        c.movePosition(QtGui.QTextCursor.EndOfLine)
        at_eol = (c.position() == current_pos)

        if self._history_index == len(self._history) or \
            not (self._history_prefix == '' and at_eol) or \
            not (self._get_edited_history(self._history_index)[:col] == input_buffer[:col]):
            self._history_prefix = input_buffer[:col]

        # Perform the search.
        self.history_previous(self._history_prefix,
                              as_prefix=not shift_down)

        # Go to the first line of the prompt for seemless history scrolling.
        # Emulate readline: keep the cursor position fixed for a prefix
        # search.
        cursor = self._get_prompt_cursor()
        if self._history_prefix:
            cursor.movePosition(QtGui.QTextCursor.Right,
                                n=len(self._history_prefix))
        else:
            cursor.movePosition(QtGui.QTextCursor.EndOfLine)
        self._set_cursor(cursor)

    # HistoryConsoleWidget
    def key_down(self, shift_down):
        """
        History on down key.
        :param shift_down:
        :return:
        """
        # Perform the search.
        replaced = self.history_next(self._history_prefix,
                                     as_prefix=not shift_down)

        # Emulate readline: keep the cursor position fixed for a prefix
        # search. (We don't need to move the cursor to the end of the buffer
        # in the other case because this happens automatically when the
        # input buffer is set.)
        if self._history_prefix and replaced:
            cursor = self.target.textCursor()
            cursor.movePosition(QtGui.QTextCursor.Start)
            cursor.movePosition(QtGui.QTextCursor.Right,
                                n=len(self._history_prefix))
            self.target.setTextCursor(cursor)
