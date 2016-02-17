from traitlets import Bool
from qtconsole.qt import QtCore

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Interactions(object):
    # Whether to override ShortcutEvents for the keybindings defined by this
    # widget (Ctrl+n, Ctrl+a, etc). Enable this if you want this widget to take
    # priority (when it has focus) over, e.g., window-level menu shortcuts.
    override_shortcuts = Bool(False)

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

    # The shortcuts defined by this widget. We need to keep track of these to
    # support 'override_shortcuts' above.
    _shortcuts = set(_ctrl_down_remap.keys()) | \
                     { QtCore.Qt.Key_C, QtCore.Qt.Key_G, QtCore.Qt.Key_O,
                       QtCore.Qt.Key_V }
