from qtconsole.qt import QtCore
from .relay_item import RelayItem, ClearOutput, InputRequest

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class OutBuffer(QtCore.QThread):
    """
    Buffer of items that correspond to blocks for output.
    """
    _target = None  # Receiver

    default_sleep = 100  # default sleep interval, in msec
    _sleep_time = 0  # sleep time in msec., updated by the thread

    item_ready = QtCore.Signal(RelayItem)

    def __init__(self, target, parent=None):
        """
        Initialize.
        :param target: target object for output and timer parent;
                        has the method target.receive: OutItem->None that outputs one item as one block.
        :param parent: parent object; recommended for efficiency of QThread.
        :return:
        """
        super(OutBuffer, self).__init__(parent)
        self._target = target
        self._sleep_time = self.default_sleep

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
        carry_over = None
        precede_output = None
        while self.isRunning():
            self.msleep(self._sleep_time)
            max_blocks = self._target.document().maximumBlockCount()
            lines_left = max_blocks if max_blocks > 0 else 1
            # if no max_blocks, then flush line by line with short brakes after each line
            total_time = 0
            while lines_left > 0 and (carry_over or not self._target.output_q.empty()):
                item = carry_over if carry_over else self._target.output_q.get()
                if isinstance(item, ClearOutput) and item.wait:
                    if precede_output:  # send preceding ClearOutput
                        self.item_ready.emit(precede_output)
                        self._target.timing_guard.acquire()
                        total_time += self._target.receive_time
                    precede_output = item
                else:  # not a ClearOutput that requires waiting or any other item
                    lines, item_first, item_rest = item.split(lines_left)
                    lines_left -= lines
                    if precede_output:
                        self.item_ready.emit(precede_output)
                        self._target.timing_guard.acquire()
                        total_time += self._target.receive_time
                        precede_output = None
                    self.item_ready.emit(item_first)
                    self._target.timing_guard.acquire()
                    total_time += self._target.receive_time
                    if not carry_over:
                        self._target.output_q.task_done()
                    carry_over = None if item_rest.empty else item_rest
            # Set the flush interval to equal the maximum time to flush this time around
            # to give the system equal time to catch up with other events.
            self._sleep_time = max(self.default_sleep, total_time)
