from qtconsole.qt import QtCore
from console_split.ui.signal_content import SignalContent

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Signaller(QtCore.QObject):
    message_ready = QtCore.Signal(SignalContent)

    def __init__(self):
        super().__init__()
        # self.message_ready = pyqtSignal(SignalContent) does not work/incorrect?

    def connect_signal(self, slot_fun):
        self.message_ready.connect(slot_fun)

    def emit_signal(self, record):
        self.message_ready.emit(record)
