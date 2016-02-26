from traitlets import Bool, Enum
from traitlets.config.configurable import LoggingConfigurable
from qtconsole.qt import QtGui, QtCore
from qtconsole.util import MetaQObjectHasTraits
from qtconsole.completion_html import CompletionHtml
from qtconsole.completion_widget import CompletionWidget
from qtconsole.completion_plain import CompletionPlain
from dispatch.source import Source
from .entry_filter import EntryFilter
from .text_config import TextConfig, get_block_plain_text

__author__ = 'Manfred Minimair <manfred@minimair.org>'


code_active_color = QtCore.Qt.black  # color used for widget's frame if in code mode
chat_active_color = QtCore.Qt.red  # color used for the widget's frame if in chat mode


def completer(who, kind):
    if kind == 'ncurses':
        return CompletionHtml(who)
    elif kind == 'droplist':
        return CompletionWidget(who)
    elif kind == 'plain':
        return CompletionPlain(who)
    else:
        return None


def to_complete(cursor):
    """
    Determine whether there is text before the cursor position that may be completed.
    :param cursor: position.
    :return: True if there is non-whitespace text immediately before the cursor.
    """
    text = get_block_plain_text(cursor.block())
    return bool(text[:cursor.columnNumber()].strip())


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

        gui_completion = Enum(['plain', 'droplist', 'ncurses'], config=True, default_value = 'ncurses',
                             help="""
                                The type of completer to use. Valid values are:

                                'plain'   : Show the available completion as a text list
                                            Below the editing area.
                                'droplist': Show the completion in a drop down list navigable
                                by the arrow keys, and from which you can select
                                completion by pressing Return.
                                'ncurses' : Show the completion as a text list which is navigable by
                                `tab` and arrow keys.
                                """)
        _completer = None

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
                self._code_changed(new=self.code_mode)
                # ensure that the frame color is set, even without change traitlets handler
            else:
                self.update_code_mode(code)
                # will initiate change traitlets handler
            self.setAcceptDrops(True)

            self._control = self  # required for completer
            self._clear_temporary_buffer = lambda: None
            self.completer = completer(self, self.gui_completion)
            self.is_complete = is_complete

            self.entry_filter = EntryFilter(self)
            self.installEventFilter(self.entry_filter)

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
            :param item: InText to be shown in the input area.
            :return:
            """
            self.clear()
            self.insertPlainText(item.text)

        @QtCore.Slot()
        def set_focus(self):
            self.setFocus()

        # traitlets handlers
        def _code_changed(self, name=None, old=None, new=None):
            """
            Set the frame color according to self.code.
            :param changed: Not used.
            :return:
            """
            new_palette = self.palette()
            new_color = code_active_color if new else chat_active_color
            new_palette.setColor(QtGui.QPalette.WindowText, new_color)
            self.setPalette(new_palette)

    return Entry
