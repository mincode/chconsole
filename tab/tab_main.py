from qtconsole.base_frontend_mixin import BaseFrontendMixin
from qtconsole.qt import QtGui, QtCore
from qtconsole.util import MetaQObjectHasTraits
from traitlets import Bool, Float
from traitlets.config.configurable import LoggingConfigurable

from tab import KernelMessage, tab_content_template, Exporter

try:
    from queue import Empty
except ImportError:
    from Queue import Empty

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

        local_kernel = False  # whether kernel is on the local machine

        # Mechanism for keeping kernel on exit required by MainWindow
        keep_kernel_on_exit = None
        exit_requested = QtCore.Signal(object)  # signal to be sent when exit is requested through the kernel
                                                # emits itself as an argument to the signal

        confirm_restart = Bool(True, config=True, help="Whether to ask for user confirmation when restarting kernel")
        is_complete_timeout = Float(0.25, config=True, help="Seconds to wait for is_complete replies from the kernel.")

        _exporter = None  # Exporter of messages to the kernel

        def __init__(self, parent=None, **kw):
            """
            Initialize the main widget.
            :param parent:
            :param kw:
            :return:
            """
            super(TabMain, self).__init__(parent, **kw)
            self._exporter = Exporter(self)
            self.main_content = tab_content_template(edit_class)(self.is_complete)
            # self.main_content.please_execute.connect(self._execute)
            # self.main_content.please_inspect.connect(self._inspect)
            # self.main_content.please_exit.connect(self._on_exit_request)
            # self.main_content.please_complete.connect(self._on_complete_request)
            self.message_arrived.connect(self.main_content.convert)

            layout = QtGui.QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.main_content)

            # Set flag for whether we are connected via localhost.
            self.local_kernel = kw.get('local_kernel', TabMain.local_kernel)

        def _started_channels(self):
            """Make a history request and load %guiref, if possible."""
            self.main_content.input_reply.connect(self.kernel_client.input)
            # 1) send clear
            ansi_clear = {'header': {'msg_type': 'stream'}, 'content': {'text': '\x0c\n', 'name': 'stdout'}}
            self.message_arrived.emit(KernelMessage(ansi_clear, from_here=True))
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
                        msg = {'header': {'msg_type': 'stream'}, 'content': {'text': text, 'name': 'stderr'}}
                        self.message_arrived.emit(KernelMessage(msg, from_here=True))
                    else:
                        text = '\nRestarting kernel...\n\n'
                        msg = {'header': {'msg_type': 'stream'}, 'content': {'text': text, 'name': 'stderr'}}
                        self.message_arrived.emit(KernelMessage(msg, from_here=True))
                else:
                    self.kernel_client.hb_channel.unpause()

            else:
                text = 'Cannot restart a Kernel I did not start'
                msg = {'header': {'msg_type': 'stream'}, 'content': {'text': text, 'name': 'stderr'}}
                self.message_arrived.emit(KernelMessage(msg, from_here=True))

        # FrontendWidget
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
                text = 'Cannot interrupt a kernel I did not start'
                msg = {'header': {'msg_type': 'stream'}, 'content': {'text': text, 'name': 'stderr'}}
                self.message_arrived.emit(KernelMessage(msg, from_here=True))

        # FrontendWidget
        def request_interrupt_kernel(self):
            self.interrupt_kernel()

        # FrontendWidget
        def _handle_kernel_died(self, since_last_heartbeat):
            """
            Handle the kernel's death (if we do not own the kernel).
            """
            self.log.warn("kernel died: %s", since_last_heartbeat)
            text = 'Kernel died'
            msg = {'header': {'msg_type': 'stream'}, 'content': {'text': text, 'name': 'stderr'}}
            self.message_arrived.emit(KernelMessage(msg, from_here=True))


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

        # @QtCore.Slot(str, int)
        # def _on_complete_request(self, code, position):
        #     """
        #     Handle a complete request.
        #     :param code: string to be completed.
        #     :param position: cursor position where to complete.
        #     :return:
        #     """
        #     self.kernel_client.complete(code=code, cursor_pos=position)

        # @QtCore.Slot(bool)
        # def _on_exit_request(self, keep_kernel_on_exit):
        #     self.keep_kernel_on_exit = True if keep_kernel_on_exit else None
        #     self.exit_requested.emit(self)

        # @QtCore.Slot(Source, int)
        # def _inspect(self, source, position):
        #     if self.kernel_client.shell_channel.is_alive():
        #         self.kernel_client.inspect(source.code, position)

        # @QtCore.Slot(Source)
        # def _execute(self, source):
        #     """
        #     Execute source.
        #     :param source: Source object.
        #     :return:
        #     """
        #     self.kernel_client.execute(source.code, silent=source.hidden)
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
