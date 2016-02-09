import time
from queue import Queue
from qtconsole.qt import QtCore
from .stoppable_thread import StoppableThread

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class BlockBuffer(StoppableThread):
    """
    Buffer of items that correspond to blocks for output.
    """
    _target = None  # Receiver
    _default_interval = 0.1  # default sleep interval, in sec
    _sleep_time = 0  # sleep time in sec.

    def __init__(self, target):
        """
        Initialize.
        :param target: target object for output and timer parent;
                        has the method target.receive: OutItem->None that outputs one item as one block.
        :return:
        """
        super(BlockBuffer, self).__init__()
        self._target = target
        self._sleep_time = self._default_interval

    def run(self):
        """
        Flush pending items.
        :return:
        """
        # When to flush? timeout after a certain time interval
        # What to flush? up to maximum block count
        # How long to wait? Heuristics: time it took last time to flush
        # The assumption for this heuristic is that the kernel sends a lot of output and there should be
        # enough time for the application to process other events then drawing output. The interval between flush
        # is chosen such that the time used for flushing is approximately equal to the time available for processing
        # other events.
        time.sleep(self._sleep_time)
        while not self.stopped():
            print('run thread; timer inactive')
            max_blocks = self._target.document().maximumBlockCount()
            block_counter = max_blocks if max_blocks > 0 else 1
            start = time.time()
            while block_counter > 0 and not self._target.output_q.empty():
                item = self._target.output_q.get()
                block_counter -= 1
                self._target.receive(item)
                self._target.output_q.task_done()
            # Set the flush interval to equal the maximum time to flush this time around
            # to give the system equal time to catch up with other events.
            self._sleep_time = max(self._default_interval, (time.time() - start) * 1000)
