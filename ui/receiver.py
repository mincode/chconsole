from queue import Queue
from functools import singledispatch
from traitlets import Integer, Unicode
from traitlets.config.configurable import LoggingConfigurable
from qtconsole.qt import QtCore, QtGui
from qtconsole.util import MetaQObjectHasTraits
from dispatch.out_item import OutItem, Stream, Input, ClearOutput
from dispatch.flush import Flush

__author__ = 'Manfred Minimair <manfred@minimair.org>'


default_in_prompt = 'In [<span class="in-prompt-number">%i</span>]: '


def _make_in_prompt(prompt_template, number=None):
    """ Given a prompt number, returns an HTML In prompt.
    """
    #from qtconsole.jupyter_widget
    try:
        body = prompt_template % number
    except TypeError:
        # allow in_prompt to leave out number, e.g. '>>> '
        from xml.sax.saxutils import escape
        body = escape(prompt_template)
    return '<span class="in-prompt">%s</span>' % body


def clear_to_beginning_of_line(cursor):
    cursor.movePosition(cursor.StartOfLine, cursor.KeepAnchor)
    cursor.insertText('')


@singledispatch
def _receive(item, receiver):
    pass
    #raise NotImplementedError


@_receive.register(Stream)
def _(item, receiver):
    if receiver.data_stream_end:
        receiver.setTextCursor(receiver.data_stream_end)
    receiver.insertPlainText(item.text)
    cursor = receiver.textCursor()
    if item.clearable:
        if item.text[-1] == '\n':
            cursor.movePosition(QtGui.QTextCursor.Up)
            cursor.movePosition(QtGui.QTextCursor.EndOfLine)
        receiver.data_stream_end = cursor if item.clearable else None
    else:
        receiver.data_stream_end = None


@_receive.register(Input)
def _(item, receiver):
    receiver.data_stream_end = None
    receiver.insertPlainText('\n')
    receiver.insertHtml(_make_in_prompt(receiver.in_prompt, item.execution_count))
    receiver.insertPlainText(item.code)
    if item.code[-1] != '\n':
        receiver.insertPlainText('\n')


@_receive.register(ClearOutput)
def _(item, receiver):
    if receiver.data_stream_end:
        cursor = receiver.data_stream_end
        clear_to_beginning_of_line(cursor)
        receiver.data_stream_end = cursor


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
            """)
        in_prompt = Unicode(default_in_prompt, config=True)

        output_q = None  # Queue
        _flush = None  # Flush

        timing_guard = None  # QSemaphore
        receive_time = 0

        data_stream_end = None  # QTextCursor, end of the last output line of stream or data

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
            self.timing_guard = QtCore.QSemaphore()
            self._flush = Flush(self, self)
            self._flush.item_ready.connect(self.on_item_ready)
            self._flush.start()

        @QtCore.Slot(OutItem)
        def on_item_ready(self, item):
            # print('receive: '+item.text)
            stamp = QtCore.QTime()
            stamp.start()
            _receive(item, self)
            self.receive_time = stamp.elapsed()
            if self.timing_guard:
                self.timing_guard.release()

        @QtCore.Slot(OutItem)
        def post(self, item):
            # _receive(item, self)
            # print('Enqueued: ' + item.text)
            self.output_q.put(item)

    return Receiver
