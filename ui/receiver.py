import sys
from queue import Queue
from functools import singledispatch
from traitlets import Integer, Unicode
from qtconsole.qt import QtCore, QtGui
from qtconsole.util import MetaQObjectHasTraits
from qtconsole.rich_text import HtmlExporter
from dispatch.out_item import OutItem, Stream, Input, ClearOutput
from dispatch.outbuffer import OutBuffer
from ui.text_config import TextConfig

__author__ = 'Manfred Minimair <manfred@minimair.org>'


default_in_prompt = 'In [<span class="in-prompt-number">%i</span>]: '


# adopted from qtconsole.console_widget
def _set_top_cursor(receiver, cursor):
    """ Scrolls the viewport so that the specified cursor is at the top.
    """
    scrollbar = receiver.verticalScrollBar()
    scrollbar.setValue(scrollbar.maximum())
    original_cursor = receiver.textCursor()
    receiver.setTextCursor(cursor)
    receiver.ensureCursorVisible()
    receiver.setTextCursor(original_cursor)


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
    receiver.insert_ansi_text(item.text, item.ansi_codes)
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
    receiver.insert_html(_make_in_prompt(receiver.in_prompt, item.execution_count))
    receiver.insert_ansi_text(item.code, item.ansi_codes)
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

        _html_exporter = None
        print_action = None  # action for printing
        export_action = None  # action for exporting
        select_all_action = None  # action for selecting all

        def __init__(self, text='', parent=None, **kwargs):
            """
            Initialize.
            :param text: initial text.
            :param parent: parent widget.
            :return:
            """
            edit_class.__init__(self, text, parent)
            TextConfig.__init__(self, **kwargs)
            # Set a monospaced font.
            self.reset_font()

            self.document().setMaximumBlockCount(self.max_blocks)
            self.output_q = Queue()
            self.timing_guard = QtCore.QSemaphore()
            self._flush = OutBuffer(self, self)
            self._flush.item_ready.connect(self.on_item_ready)
            self._flush.start()

            action = QtGui.QAction('Print', None)
            action.setEnabled(True)
            print_key = QtGui.QKeySequence(QtGui.QKeySequence.Print)
            if print_key.matches("Ctrl+P") and sys.platform != 'darwin':
                # Only override the default if there is a collision.
                # Qt ctrl = cmd on OSX, so the match gets a false positive on OSX.
                print_key = "Ctrl+Shift+P"
            action.setShortcut(print_key)
            action.setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)
            action.triggered.connect(self._print_doc)
            self.addAction(action)
            self.print_action = action

            self._html_exporter = HtmlExporter(self)
            action = QtGui.QAction('Save as HTML/XML', None)
            action.setShortcut(QtGui.QKeySequence.Save)
            action.setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)
            action.triggered.connect(self._html_exporter.export)
            self.addAction(action)
            self.export_action = action

            action = QtGui.QAction('Select All', None)
            action.setEnabled(True)
            select_all = QtGui.QKeySequence(QtGui.QKeySequence.SelectAll)
            if select_all.matches("Ctrl+A") and sys.platform != 'darwin':
                # Only override the default if there is a collision.
                # Qt ctrl = cmd on OSX, so the match gets a false positive on OSX.
                select_all = "Ctrl+Shift+A"
            action.setShortcut(select_all)
            action.setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)
            action.triggered.connect(self.selectAll)
            self.addAction(action)
            self.select_all_action = action

        def _print_doc(self, printer=None):
            """ Print the contents of the ConsoleWidget to the specified QPrinter.
            """
            if not printer:
                printer = QtGui.QPrinter()
                if QtGui.QPrintDialog(printer).exec_() != QtGui.QDialog.Accepted:
                    return
            self.print_(printer)

        def export_html(self):
            """ Shows a dialog to export HTML/XML in various formats.
            """
            self._html_exporter.export()

        # adopted from qtconsole.console_widget
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

        # adopted from qtconsole.console_widget
        def insert_html(self, html, cursor=None):
            """
            Inserts HTML using the specified cursor in such a way that future
                formatting is unaffected.
            :param html:
            :param cursor:
            :return:
            """
            cursor = cursor if cursor else self.textCursor()
            cursor.beginEditBlock()
            cursor.insertHtml(html)

            # Remark from qtconsole.console_widget:
            # After inserting HTML, the text document "remembers" it's in "html
            # mode", which means that subsequent calls adding plain text will result
            # in unwanted formatting, lost tab characters, etc. The following code
            # hacks around this behavior, which I consider to be a bug in Qt, by
            # (crudely) resetting the document's style state.
            cursor.movePosition(QtGui.QTextCursor.Left,
                                QtGui.QTextCursor.KeepAnchor)
            if cursor.selection().toPlainText() == ' ':
                cursor.removeSelectedText()
            else:
                cursor.movePosition(QtGui.QTextCursor.Right)
            cursor.insertText(' ', QtGui.QTextCharFormat())
            cursor.endEditBlock()

        # adopted from qtconsole.console_widget
        def insert_ansi_text(self, text, ansi_codes=True, cursor=None):
            cursor = cursor if cursor else self.textCursor()
            cursor.beginEditBlock()
            if ansi_codes:
                for substring in self._ansi_processor.split_string(text):
                    for act in self._ansi_processor.actions:

                        # Unlike real terminal emulators, we don't distinguish
                        # between the screen and the scrollback buffer. A screen
                        # erase request clears everything.
                        if act.action == 'erase' and act.area == 'screen':
                            cursor.select(QtGui.QTextCursor.Document)
                            cursor.removeSelectedText()

                        # Simulate a form feed by scrolling just past the last line.
                        elif act.action == 'scroll' and act.unit == 'page':
                            cursor.insertText('\n')
                            cursor.endEditBlock()
                            _set_top_cursor(self, cursor)
                            cursor.joinPreviousEditBlock()
                            cursor.deletePreviousChar()

                        elif act.action == 'carriage-return':
                            cursor.movePosition(
                                cursor.StartOfLine, cursor.KeepAnchor)

                        elif act.action == 'beep':
                            QtGui.qApp.beep()

                        elif act.action == 'backspace':
                            if not cursor.atBlockStart():
                                cursor.movePosition(
                                    cursor.PreviousCharacter, cursor.KeepAnchor)

                        elif act.action == 'newline':
                            cursor.movePosition(cursor.EndOfLine)

                    ansi_format = self._ansi_processor.get_format()

                    selection = cursor.selectedText()
                    if len(selection) == 0:
                        cursor.insertText(substring, ansi_format)
                    elif substring is not None:
                        # BS and CR are treated as a change in print
                        # position, rather than a backwards character
                        # deletion for output equivalence with (I)Python
                        # terminal.
                        if len(substring) >= len(selection):
                            cursor.insertText(substring, ansi_format)
                        else:
                            old_text = selection[len(substring):]
                            cursor.insertText(substring + old_text, ansi_format)
                            cursor.movePosition(cursor.PreviousCharacter, cursor.KeepAnchor, len(old_text))
            else:
                cursor.insertText(text)
            cursor.endEditBlock()

        @QtCore.Slot(OutItem)
        def on_item_ready(self, item):
            # print('receive: '+item.text)
            stamp = QtCore.QTime()
            stamp.start()
            _receive(item, self)
            self.receive_time = stamp.elapsed()
            if self.timing_guard:
                self.timing_guard.release()

        # @QtCore.Slot(OutItem)
        def post(self, item):
            # _receive(item, self)
            # print('Enqueued: ' + item.text)
            self.output_q.put(item)

    return Receiver
