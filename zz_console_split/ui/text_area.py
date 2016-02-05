from qtconsole.qt import QtGui, QtCore
from .text_area_parts.text_area_mixin import TextAreaMixin, post_signal_content, RichTextMixin
from .text_area_parts.plain_out_mixin import PlainOutMixin
from .text_area_parts.plain_page_mixin import PlainPageMixin
from .text_area_parts.plain_in_mixin import PlainInMixin
from .signal_content import SignalContent

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def text_area_template(editor):
    """
    :param editor: either QtGui.QTextEdit or QtGui.QPlainTextEdit
    :return:
    """
    class _TextArea(TextAreaMixin, editor):
        # Signals and slots must be here, not in TextAreaMixin
        # Signals that indicate ConsoleWidget state.
        copy_available = QtCore.Signal(bool)
        redo_available = QtCore.Signal(bool)  # so far not supported
        undo_available = QtCore.Signal(bool)  # so far not supported
        # Signal emitted when the font is changed.
        font_changed = QtCore.Signal(QtGui.QFont)

        def __init__(self, font_family, gui_completion, parent):
            editor.__init__(self, parent)
            TextAreaMixin.__init__(self, font_family, gui_completion)

        @QtCore.Slot(SignalContent)
        def insert_signal_content(self, output):
            post_signal_content(output, self, self.ansi_processor)

    class _EmptyClass(object):
        pass

    if issubclass(editor, QtGui.QTextEdit):
        _RichTextMixin = RichTextMixin
    else:
        _RichTextMixin = _EmptyClass

    class OutArea(_RichTextMixin, PlainOutMixin, _TextArea):
        def __init__(self, font_family, parent=None):
            _TextArea.__init__(self, font_family, gui_completion='', parent=parent)
            PlainOutMixin.__init__(self)
            _RichTextMixin.__init__(self)

    class PageArea(_RichTextMixin, PlainPageMixin, _TextArea):
        def __init__(self, font_family, parent=None):
            _TextArea.__init__(self, font_family, gui_completion='', parent=parent)
            PlainPageMixin.__init__(self)
            _RichTextMixin.__init__(self)

    class InArea(_RichTextMixin, PlainInMixin, _TextArea):
        def __init__(self, font_family, gui_completion='', parent=None):
            _TextArea.__init__(self, font_family, gui_completion, parent)
            PlainInMixin.__init__(self)
            _RichTextMixin.__init__(self)

    return OutArea, PageArea, InArea

PlainOutArea, PlainPageArea, PlainInArea = text_area_template(QtGui.QPlainTextEdit)
RichOutArea, RichPageArea, RichInArea = text_area_template(QtGui.QTextEdit)

