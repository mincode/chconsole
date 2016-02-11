from qtconsole.qt import QtCore
from .out_item import OutItem, ClearOutput

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Flush(QtCore.QThread):
    """
    Buffer of items that correspond to blocks for output.
    """
    _target = None  # Receiver
    _default_interval = 100  # default sleep interval, in msec
    _sleep_time = 0  # sleep time in msec.
    _carry_over = None  # item left to output from previous flush

    item_ready = QtCore.Signal(OutItem)

    def __init__(self, target, parent=None):
        """
        Initialize.
        :param target: target object for output and timer parent;
                        has the method target.receive: OutItem->None that outputs one item as one block.
        :return:
        """
        super(Flush, self).__init__(parent)
        self._target = target
        self._sleep_time = self._default_interval
        self._carry_over = None

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
        wait = None
        while self.isRunning():
            self.msleep(self._sleep_time)
            max_blocks = self._target.document().maximumBlockCount()
            lines_left = max_blocks if max_blocks > 0 else 1
            # if no max_blocks, then flush line by line with short brakes after each line
            self._target.receive_time = 0
            while lines_left > 0 and (self._carry_over or not self._target.output_q.empty()):
                # print('run thread; timer inactive; q not empty')
                item = self._carry_over if self._carry_over else self._target.output_q.get()
                if isinstance(item, ClearOutput) and item.wait:
                    wait = item
                else:
                    lines, item_first, item_rest = item.split(lines_left)
                    lines_left -= lines
                if wait:
                    self.item_ready.emit(wait)
                    wait = None
                self.item_ready.emit(item_first)
                if not self._carry_over:
                    self._target.output_q.task_done()
                self._carry_over = None if item_rest.empty else item_rest
            # Set the flush interval to equal the maximum time to flush this time around
            # to give the system equal time to catch up with other events.
            self._sleep_time = max(self._default_interval, self._target.receive_time)
