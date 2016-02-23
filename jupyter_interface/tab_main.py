from traitlets.config.configurable import LoggingConfigurable
from traitlets import Bool
from qtconsole.qt import QtGui, QtCore
from qtconsole.base_frontend_mixin import BaseFrontendMixin
from qtconsole.util import MetaQObjectHasTraits
from ui.tab_content import tab_content_template
from dispatch.message import KernelMessage
from dispatch.source import Source

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class _BaseTabWidget(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, QtGui.QWidget), {})):
    """ The base class for the main widget to be inserted into a tab of the Jupyter MainWindow object.
    """

    ###############################################################################################################
    # The following data members are required to launch qtconsole.qtconsoleapp with this widget as widget_factory:

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


def tab_main_template(edit_class):
    """
    Template for TabMain.
    :param edit_class: QTGui.QTextEdit or QtGui.QPlainTextEdit
    :return: Instantiated class.
    """
    class TabMain(_BaseTabWidget, BaseFrontendMixin):
        """ The main widget to be inserted into a tab of the Jupyter MainWindow object.
            Isolates Jupyter code from this project's code.
        """

        main_content = None  # QWidget

        message_arrived = QtCore.Signal(KernelMessage)  # signal to send a message that has arrived from the kernel

        # Mechanism for keeping kernel on exit required by MainWindow
        keep_kernel_on_exit = None
        exit_requested = QtCore.Signal(object)  # signal to be sent when exit is requested through the kernel
                                                # emits itself as an argument to the signal

        def __init__(self, parent=None, **kw):
            """
            Initialize the main widget.
            :param parent:
            :param kw:
            :return:
            """
            super(TabMain, self).__init__(parent, **kw)
            self.main_content = tab_content_template(edit_class)()
            self.main_content.please_execute.connect(self._execute)
            self.message_arrived.connect(self.main_content.dispatch)
            self.main_content.exit_requested.connect(self._on_exit_request)

            layout = QtGui.QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.main_content)

        def _started_channels(self):
            """Make a history request and load %guiref, if possible."""
            # 1) send clear
            ansi_clear = {'header': {'msg_type': 'stream'}, 'content': {'text': '\x0c\n', 'name': 'stdout'}}
            self.message_arrived.emit(KernelMessage(ansi_clear))
            # 2) send kernel info request
            # The reply will trigger %guiref load provided language=='python' (not implemented)
            # The following kernel request is masked because the kernel automatically sends the info on startup
            # self.kernel_client.kernel_info()
            # 3) load history
            self.kernel_client.history(hist_access_type='tail', n=1000)

        def _dispatch(self, msg):
            """
            Store incoming message in a queue.
            :param msg: Incoming message.
            :return:
            """
            self.message_arrived.emit(KernelMessage(msg, self.from_here(msg)))

        @QtCore.Slot(bool)
        def _on_exit_request(self, keep_kernel_on_exit):
            self.keep_kernel_on_exit = True if keep_kernel_on_exit else None
            self.exit_requested.emit(self)

        @QtCore.Slot(Source)
        def _execute(self, source):
            """
            Execute source.
            :param source: Source object.
            :return:
            """
            self.kernel_client.execute(source.code, silent=source.hidden)
            #jupyter_client.client:
            #execute(self, code, silent=False, store_history=True,
            #        user_expressions=None, allow_stdin=None, stop_on_error=True):
            # """Execute code in the kernel.
            #
            # Parameters
            # ----------
            # code : str
            #     A string of code in the kernel's language.
            #
            # silent : bool, optional (default False)
            #     If set, the kernel will execute the code as quietly possible, and
            #     will force store_history to be False.
            #
            # store_history : bool, optional (default True)
            #     If set, the kernel will store command history.  This is forced
            #     to be False if silent is True.
            #
            # user_expressions : dict, optional
            #     A dict mapping names to expressions to be evaluated in the user's
            #     dict. The expression values are returned as strings formatted using
            #     :func:`repr`.
            #
            # allow_stdin : bool, optional (default self.allow_stdin)
            #     Flag for whether the kernel can send stdin requests to frontends.
            #
            #     Some frontends (e.g. the Notebook) do not support stdin requests.
            #     If raw_input is called from code executed from such a frontend, a
            #     StdinNotImplementedError will be raised.
            #
            # stop_on_error: bool, optional (default True)
            #     Flag whether to abort the execution queue, if an exception is encountered.
            #
            # Returns
            # -------
            # The msg_id of the message sent.
            # """
    return TabMain

RichTabMain = tab_main_template(QtGui.QTextEdit)
PlainTabMain = tab_main_template(QtGui.QPlainTextEdit)
