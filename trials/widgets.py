__author__ = 'Manfred Minimair <manfred@minimair.org>'

import sys
from qtconsole.qt import QtGui, QtCore


class MainWidget(QtGui.QWidget):
    def __init__(self):
        super().__init__()

        self._view = QtGui.QTextEdit()

        view_stack = QtGui.QWidget()
        view_stack_layout = QtGui.QStackedLayout()
        view_stack.setLayout(view_stack_layout)
        view_stack_layout.addWidget(self._view)

        self._control = QtGui.QTextEdit()

        control_stack = QtGui.QWidget()
        control_stack_layout = QtGui.QStackedLayout()
        control_stack.setLayout(control_stack_layout)
        control_stack_layout.addWidget(self._control)

        self._splitter = QtGui.QSplitter()
        self._splitter.setOrientation(QtCore.Qt.Vertical)
        self._splitter.addWidget(view_stack)
        self._splitter.addWidget(control_stack)

        top_layout = QtGui.QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addWidget(self._splitter)
        self.setLayout(top_layout)


def main():
    app = QtGui.QApplication(sys.argv)
    w = MainWidget()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
