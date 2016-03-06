from qtconsole.qt import QtGui, QtCore

from ui.entry.line_prompt_filter import LinePromptFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class DecorativeFrame(QtGui.QFrame):
    content = None

    def __init__(self, parent=None):
        super(DecorativeFrame, self).__init__(parent)
        self.setFrameShape(QtGui.QFrame.Box)
        self.setLineWidth(2)
        self.setFrameShadow(QtGui.QFrame.Plain)
        layout = QtGui.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.content = QtGui.QFrame(self)
        layout.addWidget(self.content)
        self.content.setFrameShape(QtGui.QFrame.Panel)
        self.content.setLineWidth(4)
        self.content.setFrameShadow(QtGui.QFrame.Sunken)


class LinePrompt(DecorativeFrame):
    _prompt = None  # QLabel, prompt label
    _line = None  # QLineEdit for input requests

    text_input = QtCore.Signal(str)  # Emitted with read text
    line_prompt_filter = None  # eventFilter

    def __init__(self, prompt='', password=False, parent=None):
        """
        Initialize.
        :param prompt: prompt string to show
        :param password: whether input in password mode
        :param parent:
        :return:
        """
        super(LinePrompt, self).__init__(parent)
        self.hide()
        self.line_prompt_filter = LinePromptFilter(self)
        self.installEventFilter(self.line_prompt_filter)

        self._prompt = QtGui.QLabel()
        self.prompt = prompt
        self._line = QtGui.QLineEdit()
        self.password = password
        self._line.returnPressed.connect(self._on_return_pressed)

        layout = QtGui.QHBoxLayout(self.content)
        layout.addWidget(self._prompt)
        layout.addWidget(self._line)

    def showEvent(self, event):
        self.setFixedWidth((self.parent().width()*7)/8)
        horizontal = max(0, self.parent().width()-self.width())
        vertical = max(0, self.parent().height()-self.height())
        self.move(horizontal/4, vertical/2)

    @property
    def password(self):
        echo_mode = self._line.echoMode()
        return echo_mode == QtGui.QLineEdit.Password

    @password.setter
    def password(self, password=False):
        echo_mode = QtGui.QLineEdit.Password if password else QtGui.QLineEdit.Normal
        self._line.setEchoMode(echo_mode)

    @property
    def prompt(self):
        return self._prompt.text()

    @prompt.setter
    def prompt(self, text):
        self._prompt.setText(text)

    @property
    def line(self):
        return self._line.text()

    @line.setter
    def line(self, line):
        self._line.setText(line)

    def set_focus(self):
        self._line.setFocus()

    def clear(self):
        self.prompt = ''
        self.password = False
        self.line = ''

    @QtCore.Slot()
    def _on_return_pressed(self):
        self.text_input.emit(self._line.text())
        self.hide()
