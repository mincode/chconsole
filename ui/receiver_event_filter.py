from qtconsole.qt import QtCore, QtGui
from .base_event_filter import BaseEventFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class ReceiverFilter(BaseEventFilter):
    def __init__(self, target):
        super(ReceiverFilter, self).__init__(target)
