import sys

from qtconsole.qt import QtGui, QtCore

from chconsole.media.right_aligned import RightAligned


class Example(QtGui.QMainWindow):
    text_edit = None

    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):

        self.text_edit = QtGui.QTextEdit()
        self.text_edit.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        self.text_edit.setLineWidth(2)
        # self.text_edit.setAutoFillBackground(True)
        edit_fg_color = self.text_edit.palette().color(QtGui.QPalette.WindowText)

        self.setCentralWidget(self.text_edit)

        exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        #exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        status_bar = self.statusBar()

        button_insert = QtGui.QToolButton()
        button_insert.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        button_insert.setText('Insert')
        button_insert.clicked.connect(self.on_insert)
        status_bar.addPermanentWidget(button_insert)

        button_undo = QtGui.QToolButton()
        button_undo.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        button_undo.setText('Undo')
        button_undo.clicked.connect(self.on_undo)
        status_bar.addPermanentWidget(button_undo)

        cursor = self.text_edit.textCursor()
        cursor.insertText('first|')
        self.flex = RightAligned(cursor.position(), '_Second_')
        self.flex.insert(self.text_edit.document(), 11)
        cursor.insertText('|third|')
        print('after third pos: {}'.format(cursor.position()))
        self.flex2 = RightAligned(cursor.position(), '_Fourth_')
        self.flex2.insert(self.text_edit.document(), 11)
        cursor.insertText('|')

        button_show = QtGui.QToolButton()
        button_show.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        button_show.setText('Show')
        button_show.clicked.connect(self.on_show)
        status_bar.addPermanentWidget(button_show)

        button_hide = QtGui.QToolButton()
        button_hide.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        button_hide.setText('Hide')
        button_hide.clicked.connect(self.on_hide)
        status_bar.addPermanentWidget(button_hide)

        button_center = QtGui.QToolButton()
        button_center.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        button_center.setText('Center')
        button_center.clicked.connect(self.on_center)
        status_bar.addPermanentWidget(button_center)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(exitAction)

        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Main window')
        self.show()

    @QtCore.Slot()
    def on_show(self):
        self.flex.insert(self.text_edit.document(), 11)
        self.flex2.insert(self.text_edit.document(), 11)

    @QtCore.Slot()
    def on_hide(self):
        self.flex2.remove(self.text_edit.document(), 11)
        self.flex.remove(self.text_edit.document(), 11)

    @QtCore.Slot()
    def on_center(self):
        self.flex2.adjust(self.text_edit.document(), 11, 15)
        self.flex.adjust(self.text_edit.document(), 11, 15)

    @QtCore.Slot()
    def on_insert(self):
        cursor = self.text_edit.textCursor()
        cursor.insertText('0123')
        self.pos0 = cursor.position()
        # cursor.beginEditBlock()
        cursor.insertText('ABC')
        self.cursor = cursor
        # cursor.endEditBlock()

    @QtCore.Slot()
    def on_undo(self):
        # self.text_edit.undo()
        pos1 = self.cursor.position()
        self.cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, pos1-self.pos0)
        self.cursor.deleteChar()

def main():

    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
