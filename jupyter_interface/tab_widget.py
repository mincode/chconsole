from queue import Queue
from traitlets.config.configurable import LoggingConfigurable
from traitlets import Bool
from qtconsole.qt import QtGui, QtCore
from qtconsole.base_frontend_mixin import BaseFrontendMixin
from qtconsole.util import MetaQObjectHasTraits
from ui.tab_content import tab_content_template
from dispatch.relay import Relay
from ui.source import Source

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def _resize_last(splitter, fraction=4):
    sizes = splitter.sizes()
    print(str(sizes))
    total_height = sum(sizes)
    num_widgets = len(sizes)
    height_last = total_height // fraction
    height_rest = (total_height * (fraction - 1)) // fraction
    new_sizes = [height_rest for i in range(num_widgets - 1)]
    new_sizes.append(height_last)
    splitter.setSizes(new_sizes)


class _BaseTabWidget(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, QtGui.QWidget), {})):
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


def tab_widget_template(edit_class):
    """
    Template for TabWidget.
    :param edit_class: QTGui.QTextEdit or QtGui.QPlainTextEdit
    :return: Instantiated class.
    """
    class TabWidget(_BaseTabWidget, BaseFrontendMixin):
        """ The main widget to be inserted into a tab of the Jupyter MainWindow object.
            Isolates Jupyter code from this project's code.
        """

        _msg_q = None  # Queue
        main_content = None  # QWidget
        _relay = None  # Relay

        def __init__(self, parent=None, **kw):
            """
            Initialize the main widget.
            :param parent:
            :param kw:
            :return:
            """
            super(TabWidget, self).__init__(parent, **kw)
            self._msg_q = Queue()
            self.main_content = tab_content_template(edit_class)()
            # listen to messages from main content widget. main content widget has a 'please_execute' signal
            self.main_content.please_execute.connect(self._execute)
            # start relay thread to act on messages
            self._relay = Relay(self._msg_q, self.main_content, self)
            self._relay.please_output.connect(self.main_content.on_output)
            self._relay.start()
            # set layout to be the main content widget
            layout = QtGui.QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.main_content)

        def _dispatch(self, msg):
            """
            Store incoming message in a queue.
            :param msg: Incoming message.
            :return:
            """
            self._msg_q.put(msg)

        @QtCore.Slot(Source)
        def _execute(self, source):
            """
            Execute source.
            :param source: Source object.
            :return:
            """
            self.kernel_client.execute(source.code, source.hidden)

    return TabWidget

RichTabWidget = tab_widget_template(QtGui.QTextEdit)
PlainTabWidget = tab_widget_template(QtGui.QPlainTextEdit)
