from qtconsole.qt import QtCore
from qtconsole.util import MetaQObjectHasTraits
from traitlets.config.configurable import LoggingConfigurable

from messages import ExportItem

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Exporter(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, QtCore.QObject), {})):
    """
    Export messages to the kernel.
    """
    please_process = QtCore.Signal(ExportItem)

    def __init__(self, parent=None, **kwargs):
        QtCore.QObject.__init__(self, parent)
        LoggingConfigurable.__init__(self, **kwargs)

    @property
    def target(self):
        return self.parent()

    def convert(self, msg):
        print('to kernel: ' + type(msg).__name__)
        handler = getattr(self, '_handle_' + msg.type, None)
        if handler:
            handler(msg)

    def _handle_exit(self, msg):
        self.target.keep_kernel_on_exit = True if msg.keep_kernel else None
        self.target.exit_requested.emit(self.target)

    def _handle_execute(self, msg):
            self.kernel_client.execute(msg.source.code, silent=msg.source.hidden)
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

    def _handle_inspect(self, msg):
        if self.target.kernel_client.shell_channel.is_alive():
            self.target.kernel_client.inspect(msg.source.code, msg.position)

    def _handle_complete(self, msg):
        self.target.kernel_client.complete(code=msg.source.code, cursor_pos=msg.position)
