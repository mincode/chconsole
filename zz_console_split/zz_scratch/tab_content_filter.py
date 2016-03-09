from qtconsole.qt import QtCore

from standards import BaseEventFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class TabContentFilter(BaseEventFilter):
    def __init__(self, target):
        super(TabContentFilter, self).__init__(target)

    def eventFilter(self, obj, event):
        intercepted = False
        event_type = event.type()

        if event_type == QtCore.QEvent.KeyPress:
            key = event.key()

            if key in (QtCore.Qt.Key_Q, QtCore.Qt.Key_Escape):
                self.target.entry.setFocus()
                intercepted = True

        return intercepted
