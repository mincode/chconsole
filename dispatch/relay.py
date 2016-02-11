from qtconsole.qt import QtCore
from .out_item import OutItem, Stream, Input, ClearOutput

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Relay(QtCore.QThread):
    """
    Relay messages from the kernel.
    """
    _msg_q = None  # Queue
    _parent = None  # parent QWidget
    please_output = QtCore.Signal(OutItem)

    def __init__(self, msg_q, parent):
        super(Relay, self).__init__(parent)
        self._msg_q = msg_q
        self._parent = parent

    def run(self):
        """
        Run the thread processing messages.
        :return:
        """
        while self.isRunning():
            msg = self._msg_q.get()
            # process message
            print('msg_type: ' + msg['header']['msg_type'])
            print(msg)
            self._dispatch(msg)
            self._msg_q.task_done()

    def _dispatch(self, msg):
        """ Calls the frontend handler associated with the message type of the
            given message.
        """
        # from qtconsole.base_frontend_mixin
        msg_type = msg['header']['msg_type']
        # print('dispatch: ' + msg_type)
        handler = getattr(self, '_handle_' + msg_type, None)
        if handler:
            handler(msg)

    def _handle_stream(self, msg):
        content = msg['content']
        self.please_output.emit(Stream(content['text'], name=content['name']))

    def _handle_kernel_info_reply(self, msg):
        self.please_output.emit(Stream(msg['content']['banner']))
        help_links = msg['content']['help_links']
        if help_links:
            self.please_output.emit(Stream('\nHelp Links'))
            for helper in help_links:
                self.please_output.emit(Stream('\n' + helper['text'] + ': ' + helper['url']))
            self.please_output.emit(Stream('\n'))

    def _handle_execute_input(self, msg):
        """Handle an execute_input message"""
        self._parent.log.debug("execute_input: %s", msg.get('content', ''))

        content = msg['content']
        if self._parent.show_other or self._parent.from_here(msg):
            self.please_output.emit(Input(content['code'], execution_count=content['execution_count']))

    #frontend_widget
    def _handle_clear_output(self, msg):
        content = msg['content']
        if self._parent.show_other or self._parent.from_here(msg):
            self.please_output.emit(ClearOutput(wait=content.wait))

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


