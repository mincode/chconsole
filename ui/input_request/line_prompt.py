from qtconsole.qt import QtGui, QtCore
from .line_prompt_filter import LinePromptFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class LinePrompt(QtGui.QWidget):
    _prompt = None  # QLabel, prompt label
    _read = None  # QLineEdit

    text_input = QtCore.Signal(str)  # Emitted with read text
    line_prompt_filter = None  # eventFilter

    def __init__(self, prompt='', password=False, parent=None):
        """
        Initialize.
        :param parent:
        :param kw:
        :return:
        """
        QtGui.QWidget.__init__(self, parent)
        self.hide()
        self.line_prompt_filter = LinePromptFilter(self)
        self.installEventFilter(self.line_prompt_filter)

        self._prompt = QtGui.QLabel()
        self.set_prompt(prompt)
        self._read = QtGui.QLineEdit()
        self.set_password(password)
        self._read.returnPressed.connect(self._on_return_pressed)

        layout = QtGui.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._prompt)
        layout.addWidget(self._read)

    def set_password(self, password=False):
        echo_mode = QtGui.QLineEdit.Password if password else QtGui.QLineEdit.Normal
        self._read.setEchoMode(echo_mode)

    def set_prompt(self, text=''):
        self._prompt.setText(text)

    def set_focus(self):
        self._read.setFocus()

    @QtCore.Slot()
    def _on_return_pressed(self):
        self.text_input.emit(self._read.text())
        self.hide()

