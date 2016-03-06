from qtconsole.qt import QtCore
from ui.base_event_filter import BaseEventFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class HistoryFilter(BaseEventFilter):
    def __init__(self, target):
        super(HistoryFilter, self).__init__(target)

    def eventFilter(self, obj, event):
        intercepted = False
        event_type = event.type()

        if event_type == QtCore.QEvent.KeyPress:
            key = event.key()
            # if key in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            #     intercepted = True

        return intercepted