from queue import Queue
from functools import singledispatch
from qtconsole.qt import QtGui, QtCore
from traitlets import Integer
from traitlets.config.configurable import LoggingConfigurable
from qtconsole.util import MetaQObjectHasTraits
from dispatch.out_item import OutItem, OutStream
from dispatch.block_buffer import BlockBuffer

__author__ = 'Manfred Minimair <manfred@minimair.org>'


@singledispatch
def _receive(item, receiver):
    pass
    #raise NotImplementedError


@_receive.register(OutStream)
def _(item, receiver):
    cursor = receiver.textCursor()
    cursor.beginEditBlock()
    cursor.insertText(item.text)
    cursor.endEditBlock()


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
        _block_buffer = None  # BlockBuffer

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
            self._block_buffer = BlockBuffer(self)
            self._block_buffer.start()

        def receive(self, item):
            # print('receive: '+item.text)
            _receive(item, self)

        def post(self, item):
            # _receive(item, self)
            print('Enqueued: ' + item.text)
            self.output_q.put(item)

    return Receiver
