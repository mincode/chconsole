import time
from qtconsole.qt import QtGui, QtCore
from .source import Source

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class MainContent(QtGui.QSplitter):
    pager_location = 'inside'
    # Enum(['top', 'inside', 'right'], default_value='inside', config=True,
    #                  help="""
    # The type of paging to use. Valid values are:
    #
    # 'top'
    #    The pager appears on top of the console.
    # 'inside'
    #    The pager covers the area showing the commands.
    # 'right'
    #    The pager appears to the right of the console.
    # """)
    _current_pager_location = ''

    please_execute = QtCore.Signal(Source)

    _view = None
    _entry = None
    _pager = None

    _console_area = None  # QSplitter
    _view_stack = None  # QWidget
    _view_stack_layout = None  # QStackedLayout

    def __init__(self):
        super(MainContent, self).__init__(QtCore.Qt.Horizontal)

        """
        pager_top
        pager_inside   pager_right
        entry
        """

        self._console_area = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.addWidget(self._console_area)

        self._view_stack = QtGui.QWidget()
        self._view_stack_layout = QtGui.QStackedLayout()
        self._view_stack.setLayout(self._view_stack_layout)
        self._view = QtGui.QTextEdit()
        self._view_stack_layout.addWidget(self._view)

        self._entry = QtGui.QTextEdit()

        self._console_area.addWidget(self._view_stack)
        self._console_area.addWidget(self._entry)

        self._pager = QtGui.QTextEdit('This is the pager!')
        self.set_pager(self.pager_location)
        self.show_pager()

    def drop_pager(self):
        """
        Remove the pager from its current location if it exists.
        :return:
        """
        if self._pager:
            self._pager.hide()
            self._pager.setParent(None)
        self._current_pager_location = ''

    def set_pager(self, location):
        """
        Set the pager at a location.
        :param location: Location to set the pager
        :return:
        """
        self.drop_pager()
        if location == 'top':
            self._console_area.insertWidget(0, self._pager)
        elif location == 'inside':
            self._view_stack_layout.insertWidget(1, self._pager)
        else:  # location == 'right'
            self.insertWidget(1, self._pager)
        self._current_pager_location = location

    def show_pager(self):
        """
        Hide the pager.
        :return:
        """
        if self._current_pager_location == 'inside':
            self._view_stack_layout.setCurrentWidget(self._pager)
        self._pager.show()

    def hide_pager(self):
        """
        Hide the pager.
        :return:
        """
        if self._current_pager_location == 'inside':
            self._view_stack_layout.setCurrentWidget(self._view)
        self._pager.hide()
