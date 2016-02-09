from qtconsole.qt import QtCore
from .stoppable_thread import StoppableThread
from .out_item import OutItem, OutStream

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Relay(StoppableThread, QtCore.QObject):
    """
    Relay messages from the kernel.
    """
    daemon = True  # Bool

    _msg_q = None  # Queue
    _main_content = None  # MainContent

    please_output = QtCore.Signal(OutItem)

    def __init__(self, msg_q, main_content):
        super(Relay, self).__init__()
        QtCore.QObject.__init__(self)
        self._msg_q = msg_q
        self._main_content = main_content

    def run(self):
        """
        Run the thread processing messages.
        :return:
        """
        while not self.stopped():
            msg = self._msg_q.get()
            if not self.stopped():
                # process message
                print(msg)
                self._dispatch(msg)
            self._msg_q.task_done()

    def stop(self):
        """
        This can be called from the main thread to safely stop this thread.
        """
        self.stop_me()
        self.join()

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
