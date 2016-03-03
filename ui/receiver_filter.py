from qtconsole.qt import QtCore, QtGui
from .base_event_filter import BaseEventFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class ReceiverFilter(BaseEventFilter):
    def __init__(self, target):
        super(ReceiverFilter, self).__init__(target)

    def eventFilter(self, obj, event):
        intercepted = False
        event_type = event.type()

        if event_type == QtCore.QEvent.KeyPress:
            intercepted = True  # eat the key
            key = event.key()
            alt_down = event.modifiers() & QtCore.Qt.AltModifier
            shift_down = event.modifiers() & QtCore.Qt.ShiftModifier
            ctrl_down = self.control_key_down(event.modifiers())

            if event.matches(QtGui.QKeySequence.Copy):
                self.target.copy()

            elif alt_down:
                if key == QtCore.Qt.Key_Greater:
                    self.target.moveCursor(QtGui.QTextCursor.End)

                elif key == QtCore.Qt.Key_Less:
                    self.target.moveCursor(QtGui.QTextCursor.Start)

                elif key == QtCore.Qt.Key_B:
                    self.target.setTextCursor(self.target.word_start_cursor)

                elif key == QtCore.Qt.Key_F:
                    self.target.setTextCursor(self.target.word_end_cursor)

            elif ctrl_down:
                if key == QtCore.Qt.Key_O:
                    self.target.release_focus.emit()
                elif key == QtCore.Qt.Key_D:
                    self.target.please_exit.emit()

            else:
                anchor_mode = QtGui.QTextCursor.KeepAnchor if shift_down else QtGui.QTextCursor.MoveAnchor

                if key == QtCore.Qt.Key_Down:
                    self.target.moveCursor(QtGui.QTextCursor.Down, anchor_mode)
                elif key == QtCore.Qt.Key_Up:
                    self.target.moveCursor(QtGui.QTextCursor.Up, anchor_mode)
                elif key == QtCore.Qt.Key_Right:
                    self.target.moveCursor(QtGui.QTextCursor.Right, anchor_mode)
                elif key == QtCore.Qt.Key_Left:
                    self.target.moveCursor(QtGui.QTextCursor.Left, anchor_mode)

                # vi/less -like key bindings
                elif key == QtCore.Qt.Key_J:
                    new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                                QtCore.Qt.Key_Down,
                                                QtCore.Qt.NoModifier)
                    QtGui.qApp.sendEvent(self.target, new_event)

                # vi/less -like key bindings
                elif key == QtCore.Qt.Key_K:
                    new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                                QtCore.Qt.Key_Up,
                                                QtCore.Qt.NoModifier)
                    QtGui.qApp.sendEvent(self.target, new_event)

        return intercepted
