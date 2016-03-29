from qtconsole.qt import QtGui, QtCore
from .push_button import PushButton
from .toggle_button import ToggleButton

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class StatusBar(QtGui.QStatusBar):
    """
    Status bar for the main window; includes buttons for the command/chat entry field.
    """
    code_button = None
    chat_button = None
    activated = QtCore.Signal(str)

    enter_button = None
    enter_clicked = QtCore.Signal()

    frontend_button = None
    frontend_clicked = QtCore.Signal()

    kernel_button = None
    kernel_clicked = QtCore.Signal()

    def __init__(self, coding_checked=True, code_checked_color=QtCore.Qt.black, chat_checked_color=QtCore.Qt.red,
                 front_end_msg=False, kernel_msg=False,
                 parent=None):
        super(StatusBar, self).__init__(parent)
        self.chat_button = ToggleButton()
        self.code_button = ToggleButton()

        self.chat_button.initialize(not coding_checked,
                                    'Chat', 'Chat enabled', 'Enable chat',
                                    chat_checked_color, self.code_button)
        self.code_button.initialize(coding_checked,
                                    'Code', 'Coding enabled', 'Enable coding',
                                    code_checked_color, self.chat_button)

        self.addWidget(self.chat_button)
        self.addWidget(self.code_button)
        self.activated.emit(self.code_button.text)
        self.code_button.toggled.connect(self.on_code_button_toggled)

        if front_end_msg:
            self.frontend_button = PushButton('Message Frontend')
            self.frontend_button.clicked.connect(self.frontend_clicked)
            self.addPermanentWidget(self.frontend_button)

        if kernel_msg:
            self.kernel_button = PushButton('Message Kernel')
            self.kernel_button.clicked.connect(self.kernel_clicked)
            self.addPermanentWidget(self.kernel_button)

        self.enter_button = PushButton('Enter')
        self.enter_button.clicked.connect(self.enter_clicked)
        self.addPermanentWidget(self.enter_button)

    def update_current(self, name):
        code = (name == self.code_button.text)
        if self.code_button.isChecked() != code:
            self.code_button.toggle()

    @QtCore.Slot(bool)
    def on_code_button_toggled(self, checked):
        if checked:
            self.activated.emit(self.code_button.text)
        else:
            self.activated.emit(self.chat_button.text)
