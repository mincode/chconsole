from traitlets.config.configurable import LoggingConfigurable
from traitlets import Bool
from qtconsole.qt import QtGui, QtCore
from qtconsole.base_frontend_mixin import BaseFrontendMixin
from qtconsole.util import MetaQObjectHasTraits
from ui.tab_content import tab_content_template
from dispatch.message import Message

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

        message_arrived = QtCore.Signal(Message)  # signal to send a message that has arrived from the kernel

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

            layout = QtGui.QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.main_content)

        def _dispatch(self, msg):
            """
            Store incoming message in a queue.
            :param msg: Incoming message.
            :return:
            """
            self.message_arrived.emit(Message(msg, self.from_here(msg)))

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
