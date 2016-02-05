#from http://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread-in-python
import threading


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    _stop_event = None  # Event

    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop_event = threading.Event()

    def stop_me(self):
        """
        Stop this thread.
        :return:
        """
        self._stop_event.set()

    def stopped(self):
        """
        Check if the thread has been stopped.
        :return: True if the thread has been stopped.
        """
        return self._stop_event.isSet()
