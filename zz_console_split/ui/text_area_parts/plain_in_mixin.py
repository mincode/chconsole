from qtconsole.qt import QtCore, QtGui
from .base_event_filter import BaseEventFilter
from .context_menu import ContextMenu

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class PlainInMixin(object):
    def __init__(self):
        self.setAcceptDrops(True)

    def context_menu(self, pos, input_target=None, allow_paste=True):
        return ContextMenu(self, pos, self, allow_paste=True)
