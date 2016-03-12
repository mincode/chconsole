import re
from functools import singledispatch
from queue import Queue

from qtconsole.qt import QtCore, QtGui
from qtconsole.util import MetaQObjectHasTraits
from traitlets import Integer, Unicode

from _version import __version__

from messages import Stderr, Stdout, HtmlText, PageDoc, Banner, Input, Result, ClearOutput, SplitItem
from .outbuffer import OutBuffer
from standards import TextConfig
from standards import ViewportFilter, TextAreaFilter
from .receiver_filter import ReceiverFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'

default_in_prompt = 'In [<span class="in-prompt-number">%i</span>]: '
default_out_prompt = 'Out[<span class="out-prompt-number">%i</span>]: '
default_output_sep = ''
default_output_sep2 = '|'


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


@singledispatch
def _receive(item, target):
    pass
    # raise NotImplementedError


@_receive.register(Stdout)
@_receive.register(Stderr)
def _(item, target):
    cursor = target.end_cursor
    target.insert_start = cursor.position()
    target.clear_cursor = cursor if item.clearable else None

    if isinstance(item.content, HtmlText):
        target.insert_html(item.content.text, cursor)
    else:
        target.insert_ansi_text(item.content.text, item.ansi_codes and target.use_ansi, cursor)
        target.ansi_processor.reset_sgr()


@_receive.register(PageDoc)
def _(item, target):
    if hasattr(target, 'insertHtml') and item.html_stream:
        _receive(item.html_stream, target)
    else:
        _receive(item.text_stream, target)


@_receive.register(Banner)
def _(item, target):
    cursor = target.end_cursor
    target.clear_cursor = None
    stream = item.stream
    stream.content.text = target.banner + stream.content.text
    _receive(stream, target)
    if item.help_links:
        cursor.insertText('Help Links')
        for helper in item.help_links:
            target.insert_ansi_text('\n' + helper['text'] + ': ', item.ansi_codes and target.use_ansi, cursor)
            url = helper['url']
            target.insert_html('<a href="' + url + '">' + url + '</a>', cursor)
    cursor.insertText('\n')


@_receive.register(Input)
def _(item, target):
    cursor = target.end_cursor
    target.clear_cursor = None
    cursor.insertText('\n')
    target.insert_html(_make_in_prompt(target.in_prompt, item.execution_count), cursor)
    target.insert_ansi_text(item.code, item.ansi_codes and target.use_ansi, cursor)
    target.ansi_processor.reset_sgr()
    if item.code[-1] != '\n':
        cursor.insertText('\n')


@_receive.register(Result)
def _(item, target):
    cursor = target.end_cursor
    target.clear_cursor = None
    cursor.insertText(target.output_sep, cursor)
    target.insert_html(_make_out_prompt(target.out_prompt, item.execution_count), cursor)
    # JupyterWidget: If the repr is multiline, make sure we start on a new line,
    # so that its lines are aligned.
    if "\n" in item.content.text and not target.output_sep.endswith("\n"):
        cursor.insertText('\n')
    cursor.insertText(item.content.text + target.output_sep2)


@_receive.register(ClearOutput)
def _(item, target):
    if target.clear_cursor:
        pos1 = target.clear_cursor.position()
        target.clear_cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, pos1-target.insert_start)
        target.clear_cursor.deleteChar()
        target.clear_cursor = None


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
        _out_buffer = None  # OutBuffer

        timing_guard = None  # QSemaphore
        receive_time = 0

        insert_start = 0  # position of the start of the last insert that is clearable
        clear_cursor = None  # QTextCursor, used for clearing previous item received

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
        release_focus = QtCore.Signal()  # signal to release the focus
        please_exit = QtCore.Signal(bool)  # Signal when exit is requested

        def __init__(self, text='', use_ansi=True, parent=None, **kwargs):
            """
            Initialize.
            :param text: initial text.
            :param parent: parent widget.
            :return:
            """
            edit_class.__init__(self, text, parent)
            TextConfig.__init__(self, **kwargs)

            self.use_ansi = use_ansi

            self.document().setMaximumBlockCount(self.max_blocks)
            self.output_q = Queue()
            self.timing_guard = QtCore.QSemaphore()
            self._out_buffer = OutBuffer(self, self)
            self._out_buffer.item_ready.connect(self.on_item_ready)
            self._out_buffer.start()

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

        def undo_here(self):
            print('Undo command added')

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

        @QtCore.Slot(SplitItem)
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
            if hasattr(self, 'insertHtml') and page_doc.html_stream:
                doc = page_doc.html_stream.content.text
            else:
                doc = page_doc.text_stream.content.text
            return _covers(self, doc)

    return Receiver