__author__ = 'Manfred Minimair <manfred@minimair.org>'


class History:
    _history = None  # list of history items
    _history_edits = None  # dict (index, str) of edited history items
    _history_index = 0  # index of current history item
    _history_prefix = ''  # string used as prefix to only show history items with this prefix

    def __init__(self):
        self._history = []
        self._history_edits = {}

    # HistoryWidget
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
