
import sys
from qtconsole.qt import QtGui, QtCore


class Example(QtGui.QMainWindow):

    def __init__(self):
        super(Example, self).__init__()

        self.initUI()


    def initUI(self):

        text_edit = QtGui.QTextEdit()
        text_edit.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        text_edit.setLineWidth(2)
        # text_edit.setAutoFillBackground(True)
        edit_fg_color = text_edit.palette().color(QtGui.QPalette.WindowText)
        self.setCentralWidget(text_edit)

        exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        #exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        status_bar = self.statusBar()

        button_chat = QtGui.QToolButton()
        button_code = QtGui.QToolButton()

        button_chat.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        button_chat.setText('Chat')
        button_chat.setToolTip('Enable chat')

        button_chat.setAutoFillBackground(True)
        button_code.setAutoFillBackground(True)

        chat_bg_color = button_chat.palette().color(button_chat.backgroundRole())
        code_bg_color = button_code.palette().color(button_code.backgroundRole())

        # p = button_chat.palette()
        # p.setColor(QtGui.QPalette.AlternateBase, QtCore.Qt.green)
        # button_chat.setPalette(p)

        button_chat.setCheckable(True)
        button_code.setCheckable(True)

        def chat_toggled(checked):
            if checked == button_code.isChecked():
                button_code.toggle()

            if checked:
                button_chat.setToolTip('Chat enabled')
                p = button_chat.palette()
                p.setColor(button_chat.backgroundRole(), QtCore.Qt.red)
                button_chat.setPalette(p)

                p = text_edit.palette()
                p.setColor(QtGui.QPalette.WindowText, QtCore.Qt.red)
                text_edit.setPalette(p)

            else:
                button_chat.setToolTip('Enable chat')
                p = button_chat.palette()
                p.setColor(button_chat.backgroundRole(), chat_bg_color)
                button_chat.setPalette(p)

                p = text_edit.palette()
                p.setColor(QtGui.QPalette.WindowText, edit_fg_color)
                text_edit.setPalette(p)

        def code_toggled(checked):
            if checked == button_chat.isChecked():
                 button_chat.toggle()

            if checked:
                button_code.setToolTip('Code enabled')
                p = button_code.palette()
                p.setColor(button_code.backgroundRole(), QtCore.Qt.black)
                button_code.setPalette(p)
            else:
                button_code.setToolTip('Enable code')
                p = button_code.palette()
                p.setColor(button_code.backgroundRole(), code_bg_color)
                button_code.setPalette(p)

        button_chat.toggled.connect(chat_toggled)
        button_code.toggled.connect(code_toggled)

        button_chat.setChecked(False)
        button_code.setChecked(True)

        status_bar.addWidget(button_chat)

        button_code.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        button_code.setText('Code')
        status_bar.addWidget(button_code)

        button_send = QtGui.QToolButton()
        button_send.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        button_send.setText('Send')
        status_bar.addPermanentWidget(button_send)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(exitAction)

        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Main window')
        self.show()


def main():

    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
