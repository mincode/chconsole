from qtconsole.qt import QtGui, QtCore

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class PushButton(QtGui.QToolButton):
    """
    Push button with only text label.
    """
    def __init__(self, text, parent=None):
        super(PushButton, self).__init__(parent)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.setText(text)
