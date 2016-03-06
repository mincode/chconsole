import sys

from qtconsole.qt import QtCore, QtGui

from ui.standards.base_event_filter import BaseEventFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class TextAreaFilter(BaseEventFilter):
    # indicate whether resizing is currently be processed by eventFilter
    _filter_resize = None  # QSemaphore guarding multiple resizing

    # When the control key is down, these keys are mapped.
    _ctrl_down_remap = { QtCore.Qt.Key_B : QtCore.Qt.Key_Left,
                         QtCore.Qt.Key_F : QtCore.Qt.Key_Right,
                         QtCore.Qt.Key_A : QtCore.Qt.Key_Home,
                         QtCore.Qt.Key_P : QtCore.Qt.Key_Up,
                         QtCore.Qt.Key_N : QtCore.Qt.Key_Down,
                         QtCore.Qt.Key_H : QtCore.Qt.Key_Backspace, }
    if not sys.platform == 'darwin':
        # On OS X, Ctrl-E already does the right thing, whereas End moves the
        # cursor to the bottom of the buffer.
        _ctrl_down_remap[QtCore.Qt.Key_E] = QtCore.Qt.Key_End

    # Whether to override ShortcutEvents for the keybindings defined by this
    # widget (Ctrl+n, Ctrl+a, etc). Enable this if you want this widget to take
    # priority (when it has focus) over, e.g., window-level menu shortcuts.
    override_shortcuts = False  # Bool(False)

    # The shortcuts defined by this widget. We need to keep track of these to
    # support 'override_shortcuts' above.
    _shortcuts = set(_ctrl_down_remap.keys()) | \
                     { QtCore.Qt.Key_C, QtCore.Qt.Key_G, QtCore.Qt.Key_O,
                       QtCore.Qt.Key_V }

    def __init__(self, target):
        super(TextAreaFilter, self).__init__(target)
        self._filter_resize = QtCore.QSemaphore()

    def eventFilter(self, obj, event):
        """ Reimplemented to ensure a console-like behavior in the underlying
            text widgets.
        """
        intercepted = False
        event_type = event.type()
        if event_type == QtCore.QEvent.KeyPress:

            # Re-map keys for all filtered widgets.
            key = event.key()
            if self.control_key_down(event.modifiers()) and \
                    key in self._ctrl_down_remap:
                intercepted = True
                new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                            self._ctrl_down_remap[key],
                                            QtCore.Qt.NoModifier)
                QtGui.qApp.sendEvent(obj, new_event)

        # Manually adjust the scrollbars *after* a resize event is dispatched.
        elif event_type == QtCore.QEvent.Resize and self._filter_resize.tryAcquire():
            intercepted = True
            QtGui.qApp.sendEvent(obj, event)
            self.target.adjust_scrollbars()
            self._filter_resize.release()

        # Override shortcuts for all filtered widgets.
        elif event_type == QtCore.QEvent.ShortcutOverride and \
                self.override_shortcuts and \
                self.control_key_down(event.modifiers()) and \
                event.key() in self._shortcuts:
            intercepted = False
            event.accept()

        return intercepted
