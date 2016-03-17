from traitlets.config.configurable import LoggingConfigurable
from traitlets import Bool
from qtconsole.qt import QtGui, QtCore
from qtconsole.util import MetaQObjectHasTraits
from messages import ExportItem
from .named_stacked_layout import NamedStackedLayout
from .code_area import code_area_template
__author__ = 'Manfred Minimair <manfred@minimair.org>'


def entry_template(edit_class):
    """
    Template for Entry.
    :param edit_class: QTGui.QTextEdit or QtGui.QPlainTextEdit
    :return: Instantiated class.
    """
    class Entry(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, QtGui.QWidget), {})):
        """
        Text edit that has two modes, code and chat mode,
        accepting code to be executed or arbitrary text (chat messages).
        """
        code_mode = Bool(True)  # True if document contains code to be executed; rather than a chat message

        _layout = None  # NamedStackedLayout
        please_export = QtCore.Signal(ExportItem)  # tasks for the kernel
        release_focus = QtCore.Signal()  # signal release focus

        _code_area = None  # CodeArea

        def __init__(self, is_complete, use_ansi, parent=None, **kwargs):
            QtGui.QWidget.__init__(self, parent)
            LoggingConfigurable.__init__(self, **kwargs)
            self._layout = NamedStackedLayout(self)
            self._code_area = code_area_template(edit_class)(is_complete=is_complete, use_ansi=use_ansi)
            self._code_area.please_export.connect(self.please_export)
            self._code_area.release_focus.connect(self.release_focus)
            self._layout.insert_widget(0, self._code_area, 'Code')

        @property
        def history(self):
            return self._code_area.history

        def clear(self):
            """
            Clear widgets.
            :return:
            """
            self._layout.clear()

        def post(self, item):
            """
            Process the item received.
            :param item: ImportItem for the input area.
            :return:
            """
            self._layout.current_widget.post(item)

        def update_code_mode(self, code_mode):
            """
            Update code flag that indicates whether coding mode is active.
            :param code_mode: to update code flag with.
            :return:
            """
            self._layout.current_widget.update_code_mode(code_mode)

        @QtCore.Slot()
        def set_focus(self):
            """
            Set the focus to this widget.
            :return:
            """
            self.setFocus()

    return Entry
