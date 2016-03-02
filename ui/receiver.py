import re
from queue import Queue
from functools import singledispatch
from traitlets import Integer, Unicode
from qtconsole.qt import QtCore, QtGui
from qtconsole.util import MetaQObjectHasTraits
from dispatch.relay_item import RelayItem, Stream, Input, ClearOutput, ExecuteResult, Banner, PageDoc, HtmlStream
from dispatch.outbuffer import OutBuffer
from ui.text_config import TextConfig
from _version import __version__
from .standard_filters import ViewportFilter, TextAreaFilter
from .receiver_filter import ReceiverFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'

default_in_prompt = 'In [<span class="in-prompt-number">%i</span>]: '
default_out_prompt = 'Out[<span class="out-prompt-number">%i</span>]: '
default_output_sep = ''
default_output_sep2 = ''


# JupyterWidget
def _make_in_prompt(prompt_template, number=None):
    """ Given a prompt number, returns an HTML In prompt.
    """
    try:
        body = prompt_template % number
    except TypeError:
        # allow in_prompt to leave out number, e.g. '>>> '
        from xml.sax.saxutils import escape
        body = escape(prompt_template)
    return '<span class="in-prompt">%s</span>' % body


# JupyterWidget
def _make_out_prompt(prompt_template, number):
    """ Given a prompt number, returns an HTML Out prompt.
    """
    try:
        body = prompt_template % number
    except TypeError:
        # allow out_prompt to leave out number, e.g. '<<< '
        from xml.sax.saxutils import escape
        body = escape(prompt_template)
    return '<span class="out-prompt">%s</span>' % body


def clear_to_beginning_of_line(cursor):
    cursor.movePosition(cursor.StartOfLine, cursor.KeepAnchor)
    cursor.insertText('')


def _covers(edit_widget, text):
    line_height = QtGui.QFontMetrics(edit_widget.font).height()
    # print('lines: {}'.format(line_height))
    min_lines = edit_widget.viewport().height() / line_height
    return re.match("(?:[^\n]*\n){%i}" % min_lines, text)


def _valid_text_cursor(receiver):
    """
    Return the text cursor of receiver to add new text, either data_stream_end or end of the document.
    :param receiver: target object where to set the cursor.
    :return:
    """
    if receiver.data_stream_end:
        cursor = receiver.data_stream_end
    else:
        cursor = receiver.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
    return cursor


@singledispatch
def _receive(item, receiver):
    pass
    # raise NotImplementedError


@_receive.register(Stream)
def _(item, receiver):
    old_text_cursor = receiver.textCursor()
    receiver.setTextCursor(_valid_text_cursor(receiver))

    receiver.insert_ansi_text(item.text, item.ansi_codes)
    receiver.ansi_processor.reset_sgr()
    if item.clearable:
        cursor = receiver.textCursor()
        if item.text[-1] == '\n':
            cursor.movePosition(QtGui.QTextCursor.Up)
            cursor.movePosition(QtGui.QTextCursor.EndOfLine)
        receiver.data_stream_end = cursor
    else:
        receiver.data_stream_end = None

    receiver.setTextCursor(old_text_cursor)


@_receive.register(HtmlStream)
def _(item, receiver):
    old_text_cursor = receiver.textCursor()
    receiver.setTextCursor(_valid_text_cursor(receiver))

    receiver.insert_html(item.text)
    receiver.data_stream_end = receiver.textCursor() if item.clearable else None

    receiver.setTextCursor(old_text_cursor)


@_receive.register(PageDoc)
def _(item, receiver):
    old_text_cursor = receiver.textCursor()
    receiver.data_stream_end = None
    receiver.setTextCursor(_valid_text_cursor(receiver))

    if hasattr(receiver, 'insertHtml') and item.html != '':
        _receive(item.html_stream, receiver)
    else:
        _receive(item.text_stream, receiver)

    receiver.setTextCursor(old_text_cursor)


@_receive.register(Banner)
def _(item, receiver):
    old_text_cursor = receiver.textCursor()
    receiver.data_stream_end = None
    receiver.setTextCursor(_valid_text_cursor(receiver))

    stream = item.stream
    stream.text = receiver.banner + stream.text
    _receive(stream, receiver)
    if item.help_links:
        receiver.insertPlainText('Help Links')
        for helper in item.help_links:
            receiver.insert_ansi_text('\n' + helper['text'] + ': ', item.ansi_codes)
            url = helper['url']
            receiver.insert_html('<a href="' + url + '">' + url + '</a>')
    receiver.insertPlainText('\n')

    receiver.setTextCursor(old_text_cursor)


@_receive.register(Input)
def _(item, receiver):
    old_text_cursor = receiver.textCursor()
    receiver.data_stream_end = None
    receiver.setTextCursor(_valid_text_cursor(receiver))

    receiver.insertPlainText('\n')
    receiver.insert_html(_make_in_prompt(receiver.in_prompt, item.execution_count))
    receiver.insert_ansi_text(item.code, item.ansi_codes)
    receiver.ansi_processor.reset_sgr()
    if item.code[-1] != '\n':
        receiver.insertPlainText('\n')

    receiver.setTextCursor(old_text_cursor)


@_receive.register(ExecuteResult)
def _(item, receiver):
    old_text_cursor = receiver.textCursor()
    receiver.data_stream_end = None
    receiver.setTextCursor(_valid_text_cursor(receiver))

    receiver.insertPlainText(receiver.output_sep)
    receiver.insert_html(_make_out_prompt(receiver.out_prompt, item.execution_count))
    # JupyterWidget: If the repr is multiline, make sure we start on a new line,
    # so that its lines are aligned.
    if "\n" in item.text and not receiver.output_sep.endswith("\n"):
        receiver.insertPlainText('\n')
    receiver.insertPlainText(item.text + receiver.output_sep2)

    receiver.setTextCursor(old_text_cursor)


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

    class Receiver(MetaQObjectHasTraits('NewBase', (TextConfig, edit_class), {})):
        """
        Text edit that shows input and output.
        """
        max_blocks = Integer(500, config=True,
                             help="""
            The maximum number of blocks in the document before truncating the document.
            Specifying a non-positive number disables truncation (not recommended).
            """)
        in_prompt = Unicode(default_in_prompt, config=True)
        out_prompt = Unicode(default_out_prompt, config=True)

        output_q = None  # Queue
        _flush = None  # Flush

        timing_guard = None  # QSemaphore
        receive_time = 0

        data_stream_end = None  # QTextCursor, end of the last output line of stream or data

        width = Integer(81, config=True,
                        help="""The width of the command display at start time in number
            of characters (will double with `right` paging)
            """)

        height = Integer(25, config=True,
                         help="""The height of the commmand display at start time in number
            of characters (will double with `top` paging)
            """)

        output_sep = Unicode(default_output_sep, config=True)  # to be included before an execute result
        output_sep2 = Unicode(default_output_sep2, config=True)  # to be included after an execute result

        # The text to show when the kernel is (re)started; before the default kernel banner is shown.
        banner = Unicode(config=True)

        viewport_filter = None
        receiver_filter = None
        text_area_filter = None
        release_focus = QtCore.Signal()

        def __init__(self, text='', parent=None, **kwargs):
            """
            Initialize.
            :param text: initial text.
            :param parent: parent widget.
            :return:
            """
            edit_class.__init__(self, text, parent)
            TextConfig.__init__(self, **kwargs)

            self.document().setMaximumBlockCount(self.max_blocks)
            self.output_q = Queue()
            self.timing_guard = QtCore.QSemaphore()
            self._flush = OutBuffer(self, self)
            self._flush.item_ready.connect(self.on_item_ready)
            self._flush.start()

            self.setAcceptDrops(True)

            self.viewport_filter = ViewportFilter(self)
            self.viewport().installEventFilter(self.viewport_filter)
            self.receiver_filter = ReceiverFilter(self)
            self.installEventFilter(self.receiver_filter)
            self.text_area_filter = TextAreaFilter(self)
            self.installEventFilter(self.text_area_filter)

            # Text interaction
            self.setReadOnly(True)
            self.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByMouse |
                QtCore.Qt.TextSelectableByKeyboard |
                QtCore.Qt.LinksAccessibleByMouse |
                QtCore.Qt.LinksAccessibleByKeyboard)

        # ConsoleWidget
        def _banner_default(self):
            return "Chat Console {version}\n".format(version=__version__)

        # ConsoleWidget
        def sizeHint(self):
            """ Reimplemented to suggest a size that is 80 characters wide and
                25 lines high.
            """
            font_metrics = QtGui.QFontMetrics(self.font)
            margin = (self.frameWidth() +
                      self.document().documentMargin()) * 2
            style = self.style()

            # Remark from qtconsole.console:
            # Note 1: Despite my best efforts to take the various margins into
            # account, the width is still coming out a bit too small, so we include
            # a fudge factor of one character here.
            # Note 2: QFontMetrics.maxWidth is not used here or anywhere else due
            # to a Qt bug on certain Mac OS systems where it returns 0.
            width = font_metrics.width(' ') * self.width + margin
            width += style.pixelMetric(QtGui.QStyle.PM_ScrollBarExtent)

            height = font_metrics.height() * self.height + margin

            return QtCore.QSize(width, height)

        @QtCore.Slot(RelayItem)
        def on_item_ready(self, item):
            # print('receive: '+item.text)
            stamp = QtCore.QTime()
            stamp.start()
            _receive(item, self)
            self.receive_time = stamp.elapsed()
            if self.timing_guard:
                self.timing_guard.release()
            self.ensureCursorVisible()

        @QtCore.Slot()
        def set_focus(self):
            """
            Set the focus to this widget.
            :return:
            """
            self.setFocus()


        def post(self, item):
            self.output_q.put(item)

        # Adopted from ConsoleWidget
        def covers(self, page_doc):
            if hasattr(self, 'insertHtml') and page_doc.html != '':
                doc = page_doc.html
            else:
                doc = page_doc.text
            return _covers(self, doc)

    return Receiver
