from qtconsole.qt import QtCore

from standards import BaseEventFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class HistoryFilter(BaseEventFilter):
    def __init__(self, target):
        super(HistoryFilter, self).__init__(target)

    def eventFilter(self, obj, event):
        intercepted = False
        event_type = event.type()

        if event_type == QtCore.QEvent.KeyPress:
            key = event.key()
            shift_down = event.modifiers() & QtCore.Qt.ShiftModifier

            if key == QtCore.Qt.Key_Up:
                cursor_block = self.target.textCursor().block()
                first_block = self.target.document().firstBlock()
                if cursor_block == first_block:
                    self.target.history.key_up(shift_down)
                    intercepted = True

            elif key == QtCore.Qt.Key_Down:
                cursor_block = self.target.textCursor().block()
                last_block = self.target.document().lastBlock()
                if cursor_block == last_block:
                    self.target.history.key_down(shift_down)
                    intercepted = True

        return intercepted
