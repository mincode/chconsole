from functools import singledispatch

from qtconsole.qt import QtGui, QtCore
from qtconsole.util import MetaQObjectHasTraits
from traitlets import Unicode
from traitlets.config.configurable import LoggingConfigurable

from chconsole.messages import ExportItem, ClearCurrentEntry
from chconsole.standards import code_active_color, chat_active_color
from .chat_area import chat_area_template
from .code_area import code_area_template
from .named_stacked_layout import NamedStackedLayout

__author__ = 'Manfred Minimair <manfred@minimair.org>'


@singledispatch
def _post(item, target):
    target.code_area.post(item)


@_post.register(ClearCurrentEntry)
def _(item, target):
    target.current_widget.clear()


def entry_template(edit_class):
    """
    Template for Entry.
    :param edit_class: QTGui.QTextEdit or QtGui.QPlainTextEdit
    :return: Instantiated class.
    """
    class Entry(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, QtGui.QFrame), {})):
        """
        Text edit that has two modes, code and chat mode,
        accepting code to be executed or arbitrary text (chat messages).
        """
        comment_prefix = Unicode('#')  # prefix for line comments

        _layout = None  # NamedStackedLayout
        please_export = QtCore.Signal(ExportItem)  # tasks for the kernel
        release_focus = QtCore.Signal()  # signal release focus
        new_current = QtCore.Signal(str)  # name of new current widget

        code_area = None  # CodeArea
        chat_area = None  # ChatArea
        _frame_color = None  # dict: name -> color, frame color of widget

        round_table = None  # RoundTable

        def __init__(self, round_table, is_complete, use_ansi, parent=None, **kwargs):
            QtGui.QWidget.__init__(self, parent)
            LoggingConfigurable.__init__(self, **kwargs)
            self._layout = NamedStackedLayout(self)
            self._layout.currentChanged.connect(self._on_current_changed)

            self.round_table = round_table

            self._frame_color = dict()

            name = 'Code'
            self._frame_color[name] = code_active_color
            self.code_area = code_area_template(edit_class)(round_table=round_table, is_complete=is_complete,
                                                            use_ansi=use_ansi,
                                                            comment_prefix=self.comment_prefix)
            self.code_area.to_next.connect(self.move)
            self.code_area.please_export.connect(self.please_export)
            self.code_area.release_focus.connect(self.release_focus)
            self._layout.insert_widget(0, self.code_area, name)
            self.switch(name)

            name = 'Chat'
            self._frame_color[name] = chat_active_color
            self.chat_area = chat_area_template(edit_class)(round_table=round_table,
                                                            comment_prefix=self.comment_prefix)
            self.chat_area.to_next.connect(self.move)
            self.chat_area.please_export.connect(self.please_export)
            self.chat_area.release_focus.connect(self.release_focus)
            self._layout.insert_widget(0, self.chat_area, 'Chat')

            self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
            self.setLineWidth(2)

        def _on_current_changed(self, index):
            self.set_frame_color(self._frame_color[self._layout.widget(index).name])

        def set_frame_color(self, color):
            new_palette = self.palette()
            new_palette.setColor(QtGui.QPalette.WindowText, color)
            self.setPalette(new_palette)

        @property
        def history(self):
            return self.code_area.history

        @property
        def current_widget(self):
            """
            Currently active widget in stack.
            :return: active widget.
            """
            return self._layout.currentWidget()

        def clear(self):
            """
            Clear widgets.
            :return:
            """
            self._layout.clear()

        def set_read_only(self, state=False):
            """
            Set to read only mode.
            :param state: Boolean.
            :return:
            """
            self._layout.set_read_only(state)

        def post(self, item):
            """
            Process the item received.
            :param item: ImportItem for the input area.
            :return:
            """
            _post(item, self)

        @property
        def source(self):
            """
            Source object in entry area.
            :return: Source.
            """
            return self.current_widget.source

        @QtCore.Slot(str)
        def switch(self, name):
            """
            Switch to named widget.
            :param name: name of widget to switch to.
            :return:
            """
            self._layout.set_current_widget(name)
            self.set_focus()

        @QtCore.Slot()
        def set_focus(self):
            """
            Set the focus to this widget.
            :return:
            """
            self.current_widget.setFocus()

        @QtCore.Slot()
        def move(self):
            """
            Switch to the next widget.
            :return:
            """
            self._layout.move()
            self.set_focus()
            self.new_current.emit(self.current_widget.name)

    return Entry
