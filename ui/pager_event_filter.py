from qtconsole.qt import QtCore, QtGui
from .base_event_filter import BaseEventFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class PagerFilter(BaseEventFilter):
    def __init__(self, target):
        super(PagerFilter, self).__init__(target)

    def eventFilter(self, obj, event):
        intercepted = False
        event_type = event.type()

        # Handle scrolling of the vsplit pager. This hack attempts to solve
        # problems with tearing of the help text inside the pager window.  This
        # happens only on Mac OS X with both PySide and PyQt. This fix isn't
        # perfect but makes the pager more usable.
        if event_type in self.target.pager_scroll_events:
            self.target.repaint()
            intercepted = True
        elif event_type == QtCore.QEvent.KeyPress:
            key = event.key()
            alt_down = event.modifiers() & QtCore.Qt.AltModifier

            if alt_down:
                if key == QtCore.Qt.Key_Greater:
                    self.target.moveCursor(QtGui.QTextCursor.End)
                    intercepted = True

                elif key == QtCore.Qt.Key_Less:
                    self.target.moveCursor(QtGui.QTextCursor.Start)
                    intercepted = True

            elif key in (QtCore.Qt.Key_Q, QtCore.Qt.Key_Escape):
                self.target.hide()
                intercepted = False

            elif key in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return,
                         QtCore.Qt.Key_Tab):
                new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                            QtCore.Qt.Key_PageDown,
                                            QtCore.Qt.NoModifier)
                QtGui.qApp.sendEvent(self.target, new_event)
                intercepted = True

            elif key == QtCore.Qt.Key_Backspace:
                new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                            QtCore.Qt.Key_PageUp,
                                            QtCore.Qt.NoModifier)
                QtGui.qApp.sendEvent(self.target, new_event)
                intercepted = True

            # vi/less -like key bindings
            elif key == QtCore.Qt.Key_J:
                new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                            QtCore.Qt.Key_Down,
                                            QtCore.Qt.NoModifier)
                QtGui.qApp.sendEvent(self.target, new_event)
                intercepted = True

            # vi/less -like key bindings
            elif key == QtCore.Qt.Key_K:
                new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                            QtCore.Qt.Key_Up,
                                            QtCore.Qt.NoModifier)
                QtGui.qApp.sendEvent(self.target, new_event)
                intercepted = True

        return intercepted


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
