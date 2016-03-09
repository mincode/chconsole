from qtconsole.qt import QtCore

from standards import BaseEventFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class LinePromptFilter(BaseEventFilter):
    """
    Filter to catch the enter/return key to end line editing.
    """
    def __init__(self, target):
        super(LinePromptFilter, self).__init__(target)

    def eventFilter(self, obj, event):
        intercepted = False
        event_type = event.type()

        if event_type == QtCore.QEvent.KeyPress:
            key = event.key()
            if key in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
                intercepted = True

        return intercepted
