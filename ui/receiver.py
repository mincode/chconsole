from queue import Queue
from functools import singledispatch
from traitlets import Integer
from traitlets.config.configurable import LoggingConfigurable
from qtconsole.qt import QtCore
from qtconsole.util import MetaQObjectHasTraits
from dispatch.out_item import OutItem, OutStream
from dispatch.flush import Flush

__author__ = 'Manfred Minimair <manfred@minimair.org>'


@singledispatch
def _receive(item, receiver):
    pass
    #raise NotImplementedError


@_receive.register(OutStream)
def _(item, receiver):
    # cursor = receiver.textCursor()
    # cursor.beginEditBlock()
    # cursor.insertText(item.text)
    # cursor.endEditBlock()
    receiver.insertPlainText(item.text)


def receiver_template(edit_class):
    """
    Template for Receiver.
    :param edit_class: QTGui.QTextEdit or QtGui.QPlainTextEdit
    :return: Instantiated class.
    """
    class Receiver(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, edit_class), {})):
        """
        Text edit that shows input and output.
        """
        max_blocks = Integer(500, config=True,
            help="""
            The maximum number of blocks in the document before truncating the document.
            Specifying a non-positive number disables truncation (not recommended).
            """
                             )
        output_q = None  # Queue
        _flush = None  # Flush

        receive_time = 0

        def __init__(self, text='', parent=None, **kwargs):
            """
            Initialize.
            :param text: initial text.
            :param parent: parent widget.
            :return:
            """
            edit_class.__init__(self, text, parent)
            LoggingConfigurable.__init__(self, **kwargs)
            self.document().setMaximumBlockCount(self.max_blocks)
            self.output_q = Queue()
            self._flush = Flush(self)
            self._flush.item_ready.connect(self.on_item_ready)
            self._flush.start()

        @QtCore.Slot(OutItem)
        def on_item_ready(self, item):
            # print('receive: '+item.text)
            stamp = QtCore.QTime()
            stamp.start()
            _receive(item, self)
            self.receive_time += stamp.elapsed()

        def post(self, item):
            # _receive(item, self)
            # print('Enqueued: ' + item.text)
            self.output_q.put(item)

    return Receiver
