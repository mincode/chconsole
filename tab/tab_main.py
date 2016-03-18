from functools import singledispatch
from traitlets import Bool, Float
from traitlets.config.configurable import LoggingConfigurable
from qtconsole.base_frontend_mixin import BaseFrontendMixin
from qtconsole.qt import QtGui, QtCore
from qtconsole.util import MetaQObjectHasTraits
from tab import tab_content_template
from messages import Exit, Execute, Inspect, Complete, Restart, Interrupt, ClearAll, KernelMessage, TailHistory
from messages import Stderr, UserInput
from standards import Importable
from . import Importer

try:
    from queue import Empty
except ImportError:
    from Queue import Empty

__author__ = 'Manfred Minimair <manfred@minimair.org>'


@singledispatch
def _export(item, target):
    pass
    #raise NotImplementedError


@_export.register(Interrupt)
def _(item, target):
    target.request_interrupt_kernel()


@_export.register(Restart)
def _(item, target):
    if target.main_content.clear_on_kernel_restart:
        target.message_arrived.emit(ClearAll())
    target.request_restart_kernel()


@_export.register(Exit)
def _(item, target):
    target.keep_kernel_on_exit = True if item.keep_kernel else None
    target.exit_requested.emit(target)


@_export.register(UserInput)
def _(item, target):
    target.kernel_client.input(item.text)


@_export.register(TailHistory)
def _(item, target):
    target.kernel_client.history(hist_access_type='tail',n=item.length)


@_export.register(Inspect)
def _(item, target):
    if target.kernel_client.shell_channel.is_alive():
        target.kernel_client.inspect(item.source.code, item.position)


@_export.register(Complete)
def _(item, target):
    target.kernel_client.complete(code=item.source.code, cursor_pos=item.position)


@_export.register(Execute)
def _(item, target):
    target.kernel_client.execute(item.source.code, silent=item.source.hidden)
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

        message_arrived = QtCore.Signal(Importable)  # signal to send a message that has arrived from the kernel

        local_kernel = False  # whether kernel is on the local machine

        # Mechanism for keeping kernel on exit required by MainWindow
        keep_kernel_on_exit = None
        exit_requested = QtCore.Signal(object)  # signal to be sent when exit is requested through the kernel
                                                # emits itself as an argument to the signal

        confirm_restart = Bool(True, config=True, help="Whether to ask for user confirmation when restarting kernel")
        is_complete_timeout = Float(0.25, config=True, help="Seconds to wait for is_complete replies from the kernel.")

        show_other = Bool(True, config=True, help='True if messages from other clients are to be included.')
        _importer = None  # Importer

        def __init__(self, parent=None, **kw):
            """
            Initialize the main widget.
            :param parent:
            :param kw:
            :return:
            """
            super(TabMain, self).__init__(parent, **kw)

            self.main_content = tab_content_template(edit_class)(self.is_complete)
            self.main_content.please_export.connect(self.export)
            # MainContent -> export

            # Import and handle kernel messages
            # message_arrived -> Importer -> MainContent
            self._importer = Importer(self)
            self.message_arrived.connect(self._importer.convert)
            self._importer.please_process.connect(self.main_content.post)
            self._importer.please_export.connect(self.export)

            layout = QtGui.QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.main_content)

            # Set flag for whether we are connected via localhost.
            self.local_kernel = kw.get('local_kernel', TabMain.local_kernel)

        def _started_channels(self):
            """Make a history request and load %guiref, if possible."""
            # 1) send clear
            self.message_arrived.emit(ClearAll())
            # 2) send kernel info request
            # The reply will trigger %guiref load provided language=='python' (not implemented)
            # The kernel also automatically sends the info on startup
            self.kernel_client.kernel_info()
            # 3) load history
            self.kernel_client.history(hist_access_type='tail', n=1000)

        def _dispatch(self, msg):
            """
            Store incoming message in a queue.
            :param msg: Incoming message.
            :return:
            """
            self.message_arrived.emit(KernelMessage(msg, from_here=self.from_here(msg), local_kernel=self.local_kernel))

        # FrontendWidget
        def _restart_kernel(self, message, now=False):
            """ Attempts to restart the running kernel.
            """
            # FrontendWidget:
            # now should be configurable via a checkbox in the dialog.  Right
            # now at least the heartbeat path sets it to True and the manual restart
            # to False.  But those should just be the pre-selected states of a
            # checkbox that the user could override if so desired.  But I don't know
            # enough Qt to go implementing the checkbox now.

            if self.kernel_manager:
                # Pause the heart beat channel to prevent further warnings.
                self.kernel_client.hb_channel.pause()

                # Prompt the user to restart the kernel. Un-pause the heartbeat if
                # they decline. (If they accept, the heartbeat will be un-paused
                # automatically when the kernel is restarted.)
                if self.confirm_restart:
                    buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
                    result = QtGui.QMessageBox.question(self, 'Restart kernel?',
                                                        message, buttons)
                    do_restart = result == QtGui.QMessageBox.Yes
                else:
                    # confirm_restart is False, so we don't need to ask user
                    # anything, just do the restart
                    do_restart = True

                if do_restart:
                    try:
                        self.kernel_manager.restart_kernel(now=now)
                    except RuntimeError as e:
                        text = 'Error restarting kernel: %s' % e
                    else:
                        self.message_arrived.emit(ClearAll())
                        text = '\nRestarting kernel...\n'
                    self.message_arrived.emit(Stderr(text))
                else:
                    self.kernel_client.hb_channel.unpause()

            else:
                text = '\nCannot restart a Kernel I did not start\n'
                self.message_arrived.emit(Stderr(text))
                self.kernel_client.hb_channel.unpause()

        # FrontendWidget
        # required by MainWindow
        def request_restart_kernel(self):
            message = 'Are you sure you want to restart the kernel?'
            self._restart_kernel(message, now=False)

        # FrontendWidget
        def interrupt_kernel(self):
            """ Attempts to interrupt the running kernel.
            """
            if self.kernel_manager:
                self.kernel_manager.interrupt_kernel()
            else:
                text = '\nCannot interrupt a kernel I did not start\n'
                self.message_arrived.emit(Stderr(text))

        # FrontendWidget
        # required by MainWindow
        def request_interrupt_kernel(self):
            self.interrupt_kernel()

        # FrontendWidget
        def _handle_kernel_died(self, since_last_heartbeat):
            """
            Handle the kernel's death (if we do not own the kernel).
            """
            self.log.warn("kernel died: %s", since_last_heartbeat)
            text = '\nKernel died\n'
            self.message_arrived.emit(Stderr(text))


        # FrontendWidget
        def is_complete(self, source):
            """ Returns whether 'source' can be completely processed and a new
                prompt created. When triggered by an Enter/Return key press,
                'interactive' is True; otherwise, it is False.

                Returns
                -------

                (complete, indent): (bool, str)
                complete is a bool, indicating whether the input is complete or not.
                indent is the current indentation string for autoindent.
                If complete is True, indent will be '', and should be ignored.
            """
            kc = self.blocking_client
            if kc is None:
                self.log.warn("No blocking client to make is_complete requests")
                return False, u''
            msg_id = kc.is_complete(source)
            while True:
                try:
                    reply = kc.shell_channel.get_msg(block=True, timeout=self.is_complete_timeout)
                except Empty:
                    # assume incomplete output if we get no reply in time
                    return False, u''
                if reply['parent_header'].get('msg_id', None) == msg_id:
                    status = reply['content'].get('status', u'complete')
                    indent = reply['content'].get('indent', u'')
                    return status != 'incomplete', indent

        def export(self, item):
            """
            Process the item received.
            :param item: ExportItem for the kernel.
            :return:
            """
            _export(item, self)

    return TabMain

RichTabMain = tab_main_template(QtGui.QTextEdit)
PlainTabMain = tab_main_template(QtGui.QPlainTextEdit)
