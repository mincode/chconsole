from qtconsole.qt import QtGui, QtCore

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class _ToggleButton(QtGui.QToolButton):
    text = ''
    checked_tooltip = ''
    unchecked_tooltip = ''
    checked_color = None
    unchecked_color = None
    partner = None

    def __init__(self, parent=None):
        super(_ToggleButton, self).__init__(parent)

    def initialize(self, is_checked, text, checked_tooltip, unchecked_tooltip, checked_color, partner):
        self.setCheckable(True)
        self.setChecked(is_checked)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.text = text
        self.setText(self.text)
        self.checked_tooltip = checked_tooltip
        self.unchecked_tooltip = unchecked_tooltip
        self.setAutoFillBackground(True)
        self.unchecked_color = self.palette().color(self.backgroundRole())
        self.checked_color = checked_color
        self.partner = partner
        self.set_activation(self.isChecked())
        self.toggled.connect(self._on_toggled)

    def set_activation(self, checked):
        if checked:
            new_tooltip = self.checked_tooltip
            new_color = self.checked_color
        else:
            new_tooltip = self.unchecked_tooltip
            new_color = self.unchecked_color

        self.setToolTip(new_tooltip)
        new_palette = self.palette()
        new_palette.setColor(self.backgroundRole(), new_color)
        self.setPalette(new_palette)

    # Slot
    def _on_toggled(self, checked):
        if checked == self.partner.isChecked():
            self.partner.toggle()
        self.set_activation(checked)


class _PushButton(QtGui.QToolButton):
    """
    Push button with only text label.
    """
    def __init__(self, text, parent=None):
        super(_PushButton, self).__init__(parent)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.setText(text)


class StatusBar(QtGui.QStatusBar):
    """
    Status bar for the main window; includes buttons for the command/chat entry field.
    """
    code_button = None
    chat_button = None
    code_toggled = QtCore.Signal(bool)

    send_button = None
    send_clicked = QtCore.Signal()

    frontend_button = None
    frontend_clicked = QtCore.Signal()

    kernel_button = None
    kernel_clicked = QtCore.Signal()

    def __init__(self, coding_checked=True, code_checked_color=QtCore.Qt.black, chat_checked_color=QtCore.Qt.red,
                 front_end_msg=True, kernel_msg=True,
                 parent=None):
        super(StatusBar, self).__init__(parent)
        self.chat_button = _ToggleButton()
        self.code_button = _ToggleButton()

        self.chat_button.initialize(not coding_checked,
                                    'Chat', 'Chat enabled', 'Enable chat',
                                    chat_checked_color, self.code_button)
        self.code_button.initialize(coding_checked,
                                    'Code', 'Coding enabled', 'Enable coding',
                                    code_checked_color, self.chat_button)

        self.addWidget(self.chat_button)
        self.addWidget(self.code_button)
        self.code_toggled.emit(coding_checked)
        self.code_button.toggled.connect(self.code_toggled)

        if front_end_msg:
            self.frontend_button = _PushButton('Message Frontend')
            self.frontend_button.clicked.connect(self.frontend_clicked)
            self.addPermanentWidget(self.frontend_button)

        if kernel_msg:
            self.kernel_button = _PushButton('Message Kernel')
            self.kernel_button.clicked.connect(self.kernel_clicked)
            self.addPermanentWidget(self.kernel_button)

        self.send_button = _PushButton('Enter')
        self.send_button.clicked.connect(self.send_clicked)
        self.addPermanentWidget(self.send_button)

    def update_code(self, code):
        if self.code_button.isChecked() != code:
            self.code_button.toggle()
