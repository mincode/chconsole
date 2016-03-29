from qtconsole.qt import QtCore, QtGui

from chconsole.standards import BaseEventFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class PagerFilter(BaseEventFilter):
    def __init__(self, target):
        super(PagerFilter, self).__init__(target)

    def eventFilter(self, obj, event):
        intercepted = False
        event_type = event.type()

        # Handle scrolling of the vertical pager. This hack attempts to solve
        # problems with tearing of the help text inside the pager window.  This
        # happens only on Mac OS X with both PySide and PyQt. This fix isn't
        # perfect but makes the pager more usable.
        if event_type in self.target.pager_scroll_events:
            self.target.repaint()
            intercepted = True
        elif event_type == QtCore.QEvent.KeyPress:
            intercepted = True  # eat the key
            key = event.key()
            alt_down = event.modifiers() & QtCore.Qt.AltModifier
            ctrl_down = self.control_key_down(event.modifiers())

            if alt_down:
                if key == QtCore.Qt.Key_Greater:
                    self.target.moveCursor(QtGui.QTextCursor.End)

                elif key == QtCore.Qt.Key_Less:
                    self.target.moveCursor(QtGui.QTextCursor.Start)

            elif ctrl_down:
                if key == QtCore.Qt.Key_O:
                    self.target.release_focus.emit()

            elif key in (QtCore.Qt.Key_Q, QtCore.Qt.Key_Escape):
                self.target.hide()
                self.target.release_focus.emit()

            elif key in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return,
                         QtCore.Qt.Key_Tab):
                new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                            QtCore.Qt.Key_PageDown,
                                            QtCore.Qt.NoModifier)
                QtGui.qApp.sendEvent(self.target, new_event)

            elif key == QtCore.Qt.Key_Backspace:
                new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                            QtCore.Qt.Key_PageUp,
                                            QtCore.Qt.NoModifier)
                QtGui.qApp.sendEvent(self.target, new_event)

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
