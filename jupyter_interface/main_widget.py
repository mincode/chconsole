from traitlets.config.configurable import LoggingConfigurable
from traitlets import Bool
from qtconsole.qt import QtGui, QtCore
from qtconsole.base_frontend_mixin import BaseFrontendMixin
from qtconsole.util import MetaQObjectHasTraits

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class _PreMainWidget(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, QtGui.QWidget), {})):
    """ The base class for the main widget to be inserted into a tab of the Jupyter MainWindow object.
    """

    ###############################################################################################################
    # The following data members are required to launch qtconsole.qtconsoleapp with this widget as widget_factor:

    # Emitted when an exit request has been received from the kernel.
    exit_requested = QtCore.Signal(object)

    confirm_restart = Bool(True, config=True,
        help="Whether to ask for user confirmation when restarting kernel")

    ###############################################################################################################

    def __init__(self, parent=None, **kw):
        """
        Initialize the main widget.
        :param parent:
        :param kw:
        :return:
        """
        QtGui.QWidget.__init__(self, parent)
        LoggingConfigurable.__init__(self, **kw)


class MainWidget(_PreMainWidget, BaseFrontendMixin):
    """ The main widget to be inserted into a tab of the Jupyter MainWindow object.
        Isolates Jupyter code from this project's code.
    """

    def __init__(self, parent=None, **kw):
        """
        Initialize the main widget.
        :param parent:
        :param kw:
        :return:
        """
        super(MainWidget, self).__init__(parent, **kw)
