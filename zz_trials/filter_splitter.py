__author__ = 'Manfred Minimair <manfred@minimair.org>'

import sys
from qtconsole.qt import QtGui, QtCore


class KeyFilter(QtCore.QObject):
    def __init__(self):
        super().__init__()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            print('filter super: '+str(key))
            return False
        else:
            return False


class SubFilter(QtCore.QObject):
    def __init__(self):
        super().__init__()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            print('filter sub: '+str(key))
            return False
        else:
            return False


class Main(QtGui.QWidget):
    command_view = None
    command_entry = None
    splitter = None

    def __init__(self, parent=None, **kwargs):
        QtGui.QWidget.__init__(self, parent)
        self.horizontal_box = QtGui.QHBoxLayout(self)
        self.splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.horizontal_box.addWidget(self.splitter)

        self.command_view = QtGui.QTextEdit()
        self.command_view.setFrameShape(QtGui.QFrame.StyledPanel)

        self.command_entry = QtGui.QTextEdit()
        self.command_entry.setFrameShape(QtGui.QFrame.StyledPanel)

        self.splitter.addWidget(self.command_view)
        self.splitter.addWidget(self.command_entry)

        self.sub_filter = SubFilter()
        self.command_entry.installEventFilter(self.sub_filter)

        self.key_filter = KeyFilter()
        self.installEventFilter(self.key_filter)


def main():
    app = QtGui.QApplication(sys.argv)
    w = Main()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
