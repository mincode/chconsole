from qtconsole.qt import QtCore
import console_split.ui.signal_content

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Signaller(QtCore.QObject):
    message_ready = QtCore.Signal(console_split.ui.signal_content.SignalContent)

    _ansi_codes = None

    def __init__(self, ansi_codes=console_split.ui.signal_content.PROCESS_ANSI_CODES):
        super().__init__()
        # self.message_ready = pyqtSignal(SignalContent) does not work/incorrect?
        self._ansi_codes = ansi_codes

    def connect_signal(self, slot_fun):
        self.message_ready.connect(slot_fun)

    def emit_signal(self, record):
        record.ansi_codes = self._ansi_codes
        self.message_ready.emit(record)