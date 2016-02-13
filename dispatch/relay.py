from traitlets.config.configurable import LoggingConfigurable
from qtconsole.qt import QtCore
from qtconsole.util import MetaQObjectHasTraits
from .out_item import OutItem, Stream, Input, ClearOutput

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Relay(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, QtCore.QObject), {})):
    """
    Relay messages from the kernel.
    """
    please_output = QtCore.Signal(OutItem)

    def __init__(self, parent=None, **kwargs):
        QtCore.QObject.__init__(self, parent)
        LoggingConfigurable.__init__(self, **kwargs)

    def dispatch(self, msg):
        print('dispatch: ' + msg.type)
        print(msg.whole)
        handler = getattr(self, '_handle_' + msg.type, None)
        if handler and msg.show_me:
            handler(msg)

    def _handle_stream(self, msg):
        content = msg.content
        self.please_output.emit(Stream(content['text'], name=content['name']))

    def _handle_kernel_info_reply(self, msg):
        self.please_output.emit(Stream(msg.content['banner'], clearable=False))
        help_links = msg.content['help_links']
        if help_links:
            self.please_output.emit(Stream('\nHelp Links', clearable=False))
            for helper in help_links:
                self.please_output.emit(Stream('\n' + helper['text'] + ': ' + helper['url'], clearable=False))
            self.please_output.emit(Stream('\n', clearable=False))

    def _handle_execute_input(self, msg):
        """Handle an execute_input message"""
        content = msg.content
        self.log.debug("execute_input: %s", content)

        self.please_output.emit(Input(content['code'], execution_count=content['execution_count']))

    def _handle_clear_output(self, msg):
        # {'header': {'msg_type': 'clear_output'}, 'content': {'wait': False}}
        #
        # {'header': {'msg_type': 'clear_output'}, 'content': {'wait': False}}
        # {'header': {'msg_type': 'stream'}, 'content': {'name': 'stdout', 'text': 'XYZ'}}
        content = msg.content
        # print('wait: ' + str(content['wait']))
        self.please_output.emit(ClearOutput(wait=content['wait']))

# frontend_widget
#     def _handle_execute_reply(self, msg):
#         """ Handles replies for code execution.
#         """
#         self.log.debug("execute: %s", msg.get('content', ''))
#         msg_id = msg['parent_header']['msg_id']
#         info = self._request_info['execute'].get(msg_id)
#         # unset reading flag, because if execute finished, raw_input can't
#         # still be pending.
#         self._reading = False
#         # MM: hidden means silent execute request; no way for user to specify hidden but it should be possible
#         if info and info.kind == 'user' and not self._hidden:
#             # Make sure that all output from the SUB channel has been processed
#             # before writing a new prompt.
#             self.kernel_client.iopub_channel.flush()
#
#             # Reset the ANSI style information to prevent bad text in stdout
#             # from messing up our colors. We're not a true terminal so we're
#             # allowed to do this.
#             if self.ansi_codes:
#                 self._ansi_processor.reset_sgr()
#
#             content = msg['content']
#             status = content['status']
#             if status == 'ok':
#                 self._process_execute_ok(msg)
#             elif status == 'error':
#                 self._process_execute_error(msg)
#             elif status == 'aborted':
#                 self._process_execute_abort(msg)
#
#             self._show_interpreter_prompt_for_reply(msg)
#             self.executed.emit(msg)
#             self._request_info['execute'].pop(msg_id)
#         elif info and info.kind == 'silent_exec_callback' and not self._hidden:
#             self._handle_exec_callback(msg)
#             self._request_info['execute'].pop(msg_id)
#         else:
#             # does not exist
#             super(FrontendWidget, self)._handle_execute_reply(msg)
