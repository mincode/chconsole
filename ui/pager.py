from traitlets import Enum, Bool
from traitlets.config.configurable import LoggingConfigurable
from qtconsole.util import MetaQObjectHasTraits
from qtconsole.qt import QtGui

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Pager(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, QtGui.QTextEdit), {})):
    """
    The pager of the console.
    """
    location = Enum(['top', 'inside', 'right'], default_value='right', config=True,
                     help="""
    The type of paging to use. Valid values are:

    'top'
       The pager appears on top of the console.
    'inside'
       The pager covers the area showing the commands.
    'right'
       The pager appears to the right of the console.
    """)

    _is_shown = Bool(False, help='True if pager is shown.')
    _top_splitter = None  # QSplitter
    _inside_stack_layout = None  # QStackLayout
    _right_splitter = None  # QSplitter

    def __init__(self, top_splitter, inside_stack_layout, right_splitter, text='', parent=None, **kwargs):
        QtGui.QTextEdit.__init__(self, text, parent)
        LoggingConfigurable.__init__(self, **kwargs)
        self._top_splitter = top_splitter
        self._inside_stack_layout = inside_stack_layout
        self._right_splitter = right_splitter
        self._location_changed()

    # Traitlets handler
    def _location_changed(self, changed=None):
        """
        Set the pager at a location, initially or upon change of location
        :param location: Location to set the pager
        :return:
        """
        is_shown = self._is_shown
        self.setParent(None)  # ensure page is not contained in any of its location widgets
        if self.location == 'top':
            self._top_splitter.insertWidget(0, self)
        elif self.location == 'inside':
            self._inside_stack_layout.insertWidget(0, self)
        else:  # location == 'right'
            self._right_splitter.insertWidget(1, self)
        if is_shown:
            self.show()

    def show(self):
        """
        Hide the pager.
        :return:
        """
        if self.location == 'inside':
            self._inside_stack_layout.setCurrentWidget(self)
        super(QtGui.QTextEdit, self).show()
        self._is_shown = True

    def hide(self):
        """
        Hide the pager.
        :return:
        """
        if self.location == 'inside':
            self._inside_stack_layout.setCurrentIndex(0)
        super(QtGui.QTextEdit, self).hide()
        self._is_shown = False
