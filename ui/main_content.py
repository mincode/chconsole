from traitlets import Integer
from traitlets.config.configurable import LoggingConfigurable
from qtconsole.util import MetaQObjectHasTraits
from qtconsole.qt import QtGui, QtCore
from .source import Source
from ui.pager import Pager

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def _resize_last(splitter, fraction=4):
    sizes = splitter.sizes()
    total_height = sum(sizes)
    num_widgets = len(sizes)
    height_last = total_height // fraction
    height_rest = (total_height * (fraction - 1)) // fraction
    new_sizes = [height_rest for i in range(num_widgets - 1)]
    new_sizes.append(height_last)
    splitter.setSizes(new_sizes)


class MainContent(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, QtGui.QSplitter), {})):
    entry_size = Integer(5, config=True,
                         help="""
    One to this value is the proportion of the height of the whole console to the command entry field.
    """)

    please_execute = QtCore.Signal(Source)

    _view = None
    _entry = None

    _pager = None

    _console_stack = None  # QWidget
    _console_stack_layout = None  # QStackedLayout
    _console_area = None  # QSplitter

    def __init__(self, **kwargs):
        QtGui.QSplitter.__init__(self, QtCore.Qt.Horizontal)
        LoggingConfigurable.__init__(self, **kwargs)

        """
        pager_top
        pager_inside   pager_right
        entry
        """

        self._console_stack = QtGui.QWidget()
        self._console_stack_layout = QtGui.QStackedLayout()
        self._console_stack.setLayout(self._console_stack_layout)
        self.addWidget(self._console_stack)

        self._console_area = QtGui.QSplitter(QtCore.Qt.Vertical)
        self._console_stack_layout.addWidget(self._console_area)

        self._entry = QtGui.QTextEdit()
        self._view = QtGui.QTextEdit()
        self._console_area.addWidget(self._view)
        self._console_area.addWidget(self._entry)

        self._pager = Pager(self._console_area, self._console_stack_layout, self, 'This is the pager!')
        self._pager.show()

    # Qt events
    def showEvent(self, event):
        if not event.spontaneous():
            _resize_last(self._console_area, self.entry_size)
