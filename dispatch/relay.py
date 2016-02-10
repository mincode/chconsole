from qtconsole.qt import QtCore
from .out_item import OutItem, OutStream

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Relay(QtCore.QThread):
    """
    Relay messages from the kernel.
    """
    _msg_q = None  # Queue

    please_output = QtCore.Signal(OutItem)

    def __init__(self, msg_q, parent=None):
        super(Relay, self).__init__(parent)
        self._msg_q = msg_q

    def run(self):
        """
        Run the thread processing messages.
        :return:
        """
        while self.isRunning():
            msg = self._msg_q.get()
            # process message
            print(msg)
            self._dispatch(msg)
            self._msg_q.task_done()

    def _dispatch(self, msg):
        """ Calls the frontend handler associated with the message type of the
            given message.
        """
        # from qtconsole.base_frontend_mixin
        msg_type = msg['header']['msg_type']
        # print('dispatch: ' + msg_type)
        handler = getattr(self, '_handle_' + msg_type, None)
        if handler:
            handler(msg)

    def _handle_stream(self, msg):
        text = msg['content']['text']
        # print('stream: ' + text)
        self.please_output.emit(OutStream(text))
