from traitlets import Integer, Unicode
from traitlets.config.configurable import LoggingConfigurable
from qtconsole.util import MetaQObjectHasTraits
from qtconsole.qt import QtGui, QtCore
from .source import Source
from ui.pager import Pager

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def _resize_last(splitter, fraction=4):
    """
    Resize the splitter making the last widget in it 1/fraction the height of it, and the preceding
    widgets share the remaining space equally.
    :param splitter: QSplitter to be resized.
    :param fraction: Integer.
    :return:
    """
    sizes = splitter.sizes()
    total_height = sum(sizes)
    num_widgets = len(sizes)
    height_last = total_height // fraction
    height_rest = (total_height * (fraction - 1)) // fraction
    new_sizes = [height_rest for i in range(num_widgets - 1)]
    new_sizes.append(height_last)
    splitter.setSizes(new_sizes)


class TabContent(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, QtGui.QSplitter), {})):
    entry_proportion = Integer(5, config=True,
                               help="""
    1/entry_size is the height of the whole console to height of the command entry field.
    """)

    default_pager_location = Unicode('right', config=True, help='Default location of the pager: right, inside or top')

    please_execute = QtCore.Signal(Source)

    _view = None  # Area of the console where chat messages, commands and outputs are shown
    _entry = None  # Area of the console to enter commands and chat

    pager = None  # Pager object
    _pager_targets = {}  # Dictionary of target widgets where the pager can reside; see Pager

    _console_stack = None  # QWidget
    _console_stack_layout = None  # QStackedLayout
    _console_area = None  # QSplitter

    def __init__(self, **kwargs):
        QtGui.QSplitter.__init__(self, QtCore.Qt.Horizontal)
        LoggingConfigurable.__init__(self, **kwargs)

        # Layout overview:
        # pager_top
        # view  |      pager_right
        #       | pager_inside
        # entry |

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

        self._pager_targets = [
            ('right', {'target': self, 'index': 1}),
            ('top', {'target': self._console_area, 'index': 0}),
            ('inside', {'target': self._console_stack_layout, 'index': 1})
        ]

        self.pager = Pager(self._pager_targets, self.default_pager_location, 'This is the pager!')
        self.pager.hide()

    @property
    def pager_locations(self):
        """
        Available pager locations.
        :return: List of strings representing the available pager locations.
        """
        return [t[0] for t in self._pager_targets]

    # Qt events
    def showEvent(self, event):
        if not event.spontaneous():
            _resize_last(self._console_area, self.entry_proportion)
