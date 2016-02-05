from dispatch.stoppable_thread import StoppableThread

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Relay(StoppableThread):
    """
    Relay messages from the kernel.
    """
    daemon = True  # Bool

    _msg_q = None  # Queue
    _main_content = None  # MainContent

    def __init__(self, msg_q, main_content):
        super().__init__()
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
                pass
            self._msg_q.task_done()

    def stop(self):
        """
        This can be called from the main thread to safely stop this thread.
        """
        self.stop_me()
        self.join()
