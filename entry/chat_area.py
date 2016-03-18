from qtconsole.qt import QtGui, QtCore
from qtconsole.util import MetaQObjectHasTraits
from messages import Source, ExportItem
from standards import DocumentConfig, ViewportFilter, TextAreaFilter
from media import to_comment
from .chat_area_filter import ChatAreaFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def chat_area_template(edit_class):
    """
    Template for Entry.
    :param edit_class: QTGui.QTextEdit or QtGui.QPlainTextEdit
    :return: Instantiated class.
    """
    class ChatArea(MetaQObjectHasTraits('NewBase', (DocumentConfig, edit_class), {})):
        """
        Text edit that has two modes, code and chat mode,
        accepting code to be executed or arbitrary text (chat messages).
        """
        name = 'Chat'  # name of the widget

        font_changed = QtCore.Signal(QtGui.QFont)          # Signal emitted when the font is changed.

        please_export = QtCore.Signal(ExportItem)  # tasks for the kernel

        viewport_filter = None
        entry_filter = None
        text_area_filter = None

        release_focus = QtCore.Signal()
        to_next = QtCore.Signal()

        _comment_prefix = '#'  # prefix for line comments

        def __init__(self, text='', comment_prefix='#', parent=None, **kwargs):
            """
            Initialize.
            :param text: initial text.
            :param parent: parent widget.
            :param kwargs: arguments for LoggingConfigurable
            :return:
            """
            edit_class.__init__(self, text, parent)
            DocumentConfig.__init__(self, **kwargs)

            self.setFrameStyle(QtGui.QFrame.NoFrame)

            self.viewport_filter = ViewportFilter(self)
            self.viewport().installEventFilter(self.viewport_filter)
            self.entry_filter = ChatAreaFilter(self)
            self.installEventFilter(self.entry_filter)
            self.text_area_filter = TextAreaFilter(self)
            self.installEventFilter(self.text_area_filter)

            self.setAcceptDrops(True)

            # self.entry_filter = ChatAreaFilter(self)
            # self.installEventFilter(self.entry_filter)

            # Text interaction
            self.setTextInteractionFlags(QtCore.Qt.TextEditable | QtCore.Qt.TextEditorInteraction)
            self.setUndoRedoEnabled(True)
            self._comment_prefix = comment_prefix

        def _set_font(self, font):
            DocumentConfig.set_font(self, font)
            if hasattr(self, 'completer') and self.completer:
                self.completer.setFont(font)
            self.font_changed.emit(font)

        @property
        def source(self):
            """
            Get the source from the document edited.
            :return: Source object.
            """
            return Source(to_comment(self.toPlainText(), self._comment_prefix))

        @QtCore.Slot()
        def set_focus(self):
            """
            Set the focus to this widget.
            :return:
            """
            self.setFocus()

    return ChatArea
