from qtconsole.qt import QtGui, QtCore
from qtconsole.util import MetaQObjectHasTraits
from traitlets import Bool
from traitlets.config.configurable import LoggingConfigurable

from dispatch.source import Source

__author__ = 'Manfred Minimair <manfred@minimair.org>'


code_active_color = QtCore.Qt.black  # color used for widget's frame if in code mode
chat_active_color = QtCore.Qt.red  # color used for the widget's frame if in chat mode


def entry_template(edit_class):
    """
    Template for Entry.
    :param edit_class: QTGui.QTextEdit or QtGui.QPlainTextEdit
    :return: Instantiated class.
    """
    class Entry(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, edit_class), {})):
        """
        Text edit that has two modes, code and chat mode,
        accepting code to be executed or arbitrary text (chat messages).
        """
        code = Bool(True)  # True if document contains code to be executed; rather than a chat message

        def __init__(self, code=True, text='', parent=None, **kwargs):
            """
            Initialize.
            :param code: True if object should initially expect code to be executed; otherwise arbitrary text.
            :param text: initial text.
            :param parent: parent widget.
            :return:
            """
            edit_class.__init__(self, text, parent)
            LoggingConfigurable.__init__(self, **kwargs)
            self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
            self.setLineWidth(2)
            if self.code == code:
                self._code_changed(new=self.code)
                # ensure that the frame color is set, even without change traitlets handler
            else:
                self.update_code(code)
                # will initiate change traitlets handler
            self.setAcceptDrops(True)

        def update_code(self, code):
            """
            Update code flag that indicates whether coding mode is active.
            :param code: to update code flag with.
            :return:
            """
            self.code = code

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
