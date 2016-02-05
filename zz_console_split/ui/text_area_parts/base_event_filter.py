import sys
from qtconsole.qt import QtCore

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def control_key_down(modifiers, include_command=False):
    """ Given a KeyboardModifiers flags object, return whether the Control
    key is down.

    Parameters
    ----------
    include_command : bool, optional (default True)
        Whether to treat the Command key as a (mutually exclusive) synonym
        for Control when in Mac OS.
    """
    # Note that on Mac OS, ControlModifier corresponds to the Command key
    # while MetaModifier corresponds to the Control key.
    if sys.platform == 'darwin':
        down = include_command and (modifiers & QtCore.Qt.ControlModifier)
        return bool(down) ^ bool(modifiers & QtCore.Qt.MetaModifier)
    else:
        return bool(modifiers & QtCore.Qt.ControlModifier)


class BaseEventFilter(QtCore.QObject):
    area = None

    def __init__(self, area=None):
        super(BaseEventFilter, self).__init__()
        self.area = area
