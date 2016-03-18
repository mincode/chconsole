import sys
from qtconsole.qt import QtCore, QtGui
from standards import BaseEventFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class ViewportFilter(BaseEventFilter):
    def __init__(self, target):
        super(ViewportFilter, self).__init__(target)

    def eventFilter(self, obj, event):
        intercepted = False
        event_type = event.type()
        # Make middle-click paste safe. Turn off paste by default.
        if event_type == QtCore.QEvent.MouseButtonRelease and \
                event.button() == QtCore.Qt.MidButton:
            intercepted = True

        if event_type == QtCore.QEvent.MouseMove:
            intercepted = False
            anchor = self.target.anchorAt(event.pos())
            QtGui.QToolTip.showText(event.globalPos(), anchor)

        return intercepted
