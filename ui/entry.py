import os
from functools import singledispatch
from traitlets import Bool, Enum
from qtconsole.qt import QtGui, QtCore
from qtconsole.util import MetaQObjectHasTraits
from qtconsole.completion_widget import CompletionWidget
from dispatch.source import Source
from .entry_filter import EntryFilter
from .text_config import TextConfig
from dispatch.relay_item import InText, CompleteItems

__author__ = 'Manfred Minimair <manfred@minimair.org>'


code_active_color = QtCore.Qt.black  # color used for widget's frame if in code mode
chat_active_color = QtCore.Qt.red  # color used for the widget's frame if in chat mode


@singledispatch
def _receive(item, receiver):
    pass
    #raise NotImplementedError


@_receive.register(InText)
def _(item, receiver):
    receiver.clear()
    receiver.insertPlainText(item.text)


@_receive.register(CompleteItems)
def _(item, receiver):
    receiver.process_complete(item)


def entry_template(edit_class):
    """
    Template for Entry.
    :param edit_class: QTGui.QTextEdit or QtGui.QPlainTextEdit
    :return: Instantiated class.
    """
    class Entry(MetaQObjectHasTraits('NewBase', (TextConfig, edit_class), {})):
        """
        Text edit that has two modes, code and chat mode,
        accepting code to be executed or arbitrary text (chat messages).
        """
        code_mode = Bool(True)  # True if document contains code to be executed; rather than a chat message

        execute_on_complete_input = Bool(True, config=True,
            help="""Whether to automatically execute on syntactically complete input.

            If False, Shift-Enter is required to submit each execution.
            Disabling this is mainly useful for non-Python kernels,
            where the completion check would be wrong.
            """
        )

        is_complete = None  # function str->(bool, str) that checks whether the input is complete code
        please_execute = QtCore.Signal()  # ask for execution of source

        viewport_filter = None
        entry_filter = None
        text_area_filter = None
        release_focus = QtCore.Signal()

        # Signal requesting completing code str ad cursor position int.
        please_complete = QtCore.Signal(str, int)

        completer = None  # completion object

        def __init__(self, is_complete=None, code=True, text='', parent=None, **kwargs):
            """
            Initialize.
            :param is_complete: function str->(bool, str) that checks whether the input is complete code
            :param code: True if object should initially expect code to be executed; otherwise arbitrary text.
            :param text: initial text.
            :param parent: parent widget.
            :param kwargs: arguments for LoggingConfigurable
            :return:
            """
            edit_class.__init__(self, text, parent)
            TextConfig.__init__(self, **kwargs)
            self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
            self.setLineWidth(2)
            if self.code_mode == code:
                self._code_mode_changed(new=self.code_mode)
                # ensure that the frame color is set, even without change traitlets handler
            else:
                self.update_code_mode(code)
                # will initiate change traitlets handler
            self.setAcceptDrops(True)

            self._control = self  # required for completer
            self._clear_temporary_buffer = lambda: None
            self.completer = CompletionWidget(self)
            self.is_complete = is_complete

            self.entry_filter = EntryFilter(self)
            self.installEventFilter(self.entry_filter)

            # Text interaction
            self.setTextInteractionFlags(QtCore.Qt.TextEditable | QtCore.Qt.TextEditorInteraction)

        def update_code_mode(self, code_mode):
            """
            Update code flag that indicates whether coding mode is active.
            :param code_mode: to update code flag with.
            :return:
            """
            self.code_mode = code_mode

        @property
        def source(self):
            """
            Get the source from the document edited.
            :return: Source object.
            """
            return Source(self.toPlainText())

        def post(self, item):
            """
            Process the item received.
            :param item: RelayItem for the input area.
            :return:
            """
            _receive(item, self)

        @QtCore.Slot()
        def set_focus(self):
            """
            Set the focus to this widget.
            :return:
            """
            self.setFocus()

        # traitlets handler
        def _code_mode_changed(self, name=None, old=None, new=None):
            """
            Set the frame color according to self.code.
            :param changed: Not used.
            :return:
            """
            new_palette = self.palette()
            new_color = code_active_color if new else chat_active_color
            new_palette.setColor(QtGui.QPalette.WindowText, new_color)
            self.setPalette(new_palette)

        def request_complete(self, cursor):
            """
            Request completion of document text at cursor.
            :param cursor:
            :return:
            """
            self.please_complete.emit(self.toPlainText(), cursor.position())

        # JupyterWidget
        def process_complete(self, items):
            cursor = self.textCursor()
            matches = items.matches
            start = items.start
            end = items.end
            start = max(start, 0)
            end = max(end, start)

            # Move the control's cursor to the desired end point
            cursor_pos = self.textCursor().position()
            if end < cursor_pos:
                cursor.movePosition(QtGui.QTextCursor.Left,
                                    n=(cursor_pos - end))
            elif end > cursor_pos:
                cursor.movePosition(QtGui.QTextCursor.Right,
                                    n=(end - cursor_pos))
            # This line actually applies the move to control's cursor
            self.setTextCursor(cursor)

            offset = end - start
            # Move the local cursor object to the start of the match and
            # complete.
            cursor.movePosition(QtGui.QTextCursor.Left, n=offset)
            self._complete_with_items(cursor, matches)

        # ConsoleWidget
        def _complete_with_items(self, cursor, items):
            """
            Complete code at a given location.
            :param cursor: cursor where completion is performed.
            :param items: list of items that can serve for completion.
            :return:
            """
            self.completer.cancel_completion()

            if len(items) == 1:
                cursor.setPosition(self.textCursor().position(),
                                   QtGui.QTextCursor.KeepAnchor)
                cursor.insertText(items[0])

            elif len(items) > 1:
                current_pos = self.textCursor().position()
                prefix = os.path.commonprefix(items)
                if prefix:
                    cursor.setPosition(current_pos, QtGui.QTextCursor.KeepAnchor)
                    cursor.insertText(prefix)

                cursor.movePosition(QtGui.QTextCursor.Left, n=len(prefix))
                self.completer.show_items(cursor, items)

    return Entry
