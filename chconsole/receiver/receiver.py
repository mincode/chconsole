import re
from functools import singledispatch
from queue import Queue

from qtconsole.qt import QtCore, QtGui
from qtconsole.util import MetaQObjectHasTraits
from traitlets import Integer, Unicode

from chconsole._version import __version__
from chconsole.media import register_qimage, is_comment, de_comment, TextRegister
from chconsole.messages import ExportItem, AtomicText, SvgXml, Jpeg, Png, SplitText, LaTeX, to_qimage
from chconsole.messages import Stderr, Stdout, HtmlText, PageDoc, Banner, Input, Result, ClearOutput, SplitItem
from chconsole.standards import DocumentConfig
from chconsole.standards import ViewportFilter, TextAreaFilter
from .outbuffer import OutBuffer
from .receiver_filter import ReceiverFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'

default_in_prompt = 'In [<span class="in-prompt-number">%i</span>]: '
default_chat_prompt = 'In [<span class="in-prompt-number">%i</span>]# '
default_out_prompt = 'Out[<span class="out-prompt-number">%i</span>]: '
default_output_sep = ''
default_output_sep2 = '\n'


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


def _covers(edit_widget, text):
    line_height = QtGui.QFontMetrics(edit_widget.font).height()
    min_lines = edit_widget.viewport().height() / line_height
    return re.match("(?:[^\n]*\n){%i}" % min_lines, text)


def _insert_stream_content(target, item, cursor):
    img = item.content.get(Jpeg)
    # RichJupyterWidget:
    # Do we support jpg?
    # it seems that sometime jpg support is a plugin of QT, so try to assume
    # it is not always supported.
    jpeg_supported = QtCore.QByteArray(b'jpeg') in QtGui.QImageReader.supportedImageFormats()
    if not img or not jpeg_supported:
        img = item.content.get((SvgXml, Png, LaTeX))
    if img and isinstance(target, QtGui.QTextEdit):
        #Test:
        # from IPython.display import Image
        # Image(filename='../yy_testing/squirrel.jpg')
        #
        # from IPython.display import Image
        # Image(filename='../yy_testing/baby-squirrel.png')

        cursor.insertText('\n')
        try:
            qimage = to_qimage(img)
        except ValueError:
            _receive(Stderr('Received invalid image/latex data.\n'), target)
        else:
            image_format = register_qimage(target.document(), qimage)
            target.insert_qimage(image_format, cursor)
            if isinstance(img, SvgXml):
                target.name_to_svg_map[image_format.name()] = img
    else:
        html = item.content.get(HtmlText)
        if html:
            target.insert_html(html.text, cursor)
        else:
            regular = item.content.get((AtomicText, SplitText))
            if regular:
                target.insert_ansi_text(regular.text, regular.ansi_codes and target.use_ansi, cursor)
                target.ansi_processor.reset_sgr()


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

    _insert_stream_content(target, item, cursor)


@_receive.register(PageDoc)
def _(item, target):
    if hasattr(target, 'insertHtml') and item.html_stream:
        _receive(item.html_stream, target)
    else:
        _receive(item.text_stream, target)


@_receive.register(Banner)
def _(item, target):
    if target.show_banner.tryAcquire():
        cursor = target.end_cursor
        target.clear_cursor = None
        stream = item.stream
        stream.content.text = target.banner + stream.content.text
        _receive(stream, target)
        if item.help_links:
            cursor.insertText('\nHelp Links')
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
    target.text_register.append(cursor.position(), item.username, style='in-prompt')

    if item.code and is_comment(item.code):
        in_prompt = _make_in_prompt(target.chat_prompt, item.execution_count)
        target.insert_html(in_prompt, cursor)
        if len(item.code.split('\n')) != 1:
            cursor.insertText('\n')
        target.insert_ansi_text(de_comment(item.code), item.ansi_codes and target.use_ansi, cursor)
        target.ansi_processor.reset_sgr()
    else:
        before_prompt = cursor.position()
        in_prompt = _make_in_prompt(target.in_prompt, item.execution_count)
        target.insert_html(in_prompt, cursor)
        after_prompt = cursor.position()
        target.highlighter.enable(after_prompt-before_prompt)
        if item.code:
            target.insert_ansi_text(item.code, item.ansi_codes and target.use_ansi, cursor)
            target.ansi_processor.reset_sgr()
        target.highlighter.disable()
    if item.code and item.code[-1] != '\n':
        cursor.insertText('\n')


@_receive.register(Result)
def _(item, target):
    cursor = target.end_cursor
    target.clear_cursor = None
    cursor.insertText(target.output_sep)
    target.text_register.append(cursor.position())
    target.insert_html(_make_out_prompt(target.out_prompt, item.execution_count), cursor)
    # JupyterWidget: If the repr is multiline, make sure we start on a new line,
    # so that its lines are aligned.
    if "\n" in item.content.text and not target.output_sep.endswith("\n"):
        cursor.insertText('\n')
    _insert_stream_content(target, item, cursor)
    cursor.insertText(target.output_sep2)


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

    class Receiver(MetaQObjectHasTraits('NewBase', (DocumentConfig, edit_class), {})):
        """
        Text edit that shows input and output.
        """
        max_blocks = Integer(500, config=True,
                             help="""
            The maximum number of blocks in the document before truncating the document.
            Specifying a non-positive number disables truncation (not recommended).
            """)
        in_prompt = Unicode(default_in_prompt, config=True)
        chat_prompt = Unicode(default_chat_prompt, config=True)
        out_prompt = Unicode(default_out_prompt, config=True)

        text_register = None  # TextRegister for code input and output lines

        output_q = None  # Queue
        _out_buffer = None  # OutBuffer

        timing_guard = None  # QSemaphore
        receive_time = 0

        show_banner = None  # QSemaphore; allow showing the banner only once

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

        please_export = QtCore.Signal(ExportItem)  # signal items to be handled by the kernel

        def __init__(self, text='', use_ansi=True, show_users=False, parent=None, **kwargs):
            """
            Initialize.
            :param text: initial text.
            :param use_ansi: whether to use ansi codes in output.
            :param show_users: whether to show user names in command listings.
            :param parent: parent widget.
            :return:
            """
            edit_class.__init__(self, text, parent)
            DocumentConfig.__init__(self, **kwargs)

            self.use_ansi = use_ansi
            self.text_register = TextRegister(self, visible=show_users)

            # Setting a positive maximum block count will automatically
            # disable the undo/redo history
            self.document().setMaximumBlockCount(self.max_blocks)
            self.output_q = Queue()
            self.timing_guard = QtCore.QSemaphore()
            self._out_buffer = OutBuffer(self, self)
            self._out_buffer.item_ready.connect(self.on_item_ready)
            self._out_buffer.start()

            self.show_banner = QtCore.QSemaphore(1)

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
