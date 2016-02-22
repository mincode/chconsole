from traitlets.config.configurable import LoggingConfigurable
from qtconsole.qt import QtCore
from qtconsole.util import MetaQObjectHasTraits
from .relay_item import RelayItem, Stream, Input, ClearOutput, PageDoc, EditFile, ExitRequested, InText

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Relay(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, QtCore.QObject), {})):
    """
    Relay messages from the kernel.
    """
    please_process = QtCore.Signal(RelayItem)

    _payload_source_edit = 'edit_magic'
    _payload_source_exit = 'ask_exit'
    _payload_source_next_input = 'set_next_input'
    _payload_source_page = 'page'

    def __init__(self, parent=None, **kwargs):
        QtCore.QObject.__init__(self, parent)
        LoggingConfigurable.__init__(self, **kwargs)

        self._payload_handlers = {
            self._payload_source_edit : self._handle_payload_edit,
            self._payload_source_exit : self._handle_payload_exit,
            self._payload_source_page : self._handle_payload_page,
            self._payload_source_next_input : self._handle_payload_next_input }

    def dispatch(self, msg):
        print('dispatch: ' + msg.type)
        print(msg.whole)
        handler = getattr(self, '_handle_' + msg.type, None)
        if handler and msg.show_me:
            handler(msg)

    def _handle_stream(self, msg):
        content = msg.content
        self.please_process.emit(Stream(content['text'], name=content['name']))

    def _handle_kernel_info_reply(self, msg):
        self.please_process.emit(Stream(msg.content['banner'], clearable=False))
        help_links = msg.content['help_links']
        if help_links:
            self.please_process.emit(Stream('\nHelp Links', clearable=False))
            for helper in help_links:
                self.please_process.emit(Stream('\n' + helper['text'] + ': ' + helper['url'], clearable=False))
            self.please_process.emit(Stream('\n', clearable=False))

    def _handle_execute_input(self, msg):
        """Handle an execute_input message"""
        content = msg.content
        self.log.debug("execute_input: %s", content)

        self.please_process.emit(Input(content['code'], execution_count=content['execution_count']))

    def _handle_clear_output(self, msg):
        # {'header': {'msg_type': 'clear_output'}, 'content': {'wait': False}}
        #
        # {'header': {'msg_type': 'clear_output'}, 'content': {'wait': False}}
        # {'header': {'msg_type': 'stream'}, 'content': {'name': 'stdout', 'text': 'XYZ'}}
        content = msg.content
        # print('wait: ' + str(content['wait']))
        self.please_process.emit(ClearOutput(wait=content['wait']))

    def _handle_display_data(self, msg):
        data = msg.content['data']
        # metadata = msg.content['metadata']
        if 'text/plain' in data:
            self.please_process.emit(Stream(data['text/plain'], name='stdout'))

# frontend_widget
    def _handle_execute_reply(self, msg):
        self.log.debug("execute: %s", msg.content)
#         msg_id = msg['parent_header']['msg_id']
#         info = self._request_info['execute'].get(msg_id)
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
        status = msg.content['status']
        if status == 'ok':
            self._process_execute_ok(msg)
        elif status == 'error':
            # self._process_execute_error(msg)
            pass
        elif status == 'aborted':
            # self._process_execute_abort(msg)
            pass
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

    # FrontendWidget
    def _process_execute_ok(self, msg):
        """ Process a reply for a successful execution request.
        """
        payload = msg.content.get('payload', [])
        for item in payload:
            if not self._process_execute_payload(item):
                warning = 'Warning: received unknown payload of type %s'
                print(warning % repr(item['source']))

    # JupyterWidget
    def _process_execute_payload(self, item):
        """ Reimplemented to dispatch payloads to handler methods.
        """
        handler = self._payload_handlers.get(item['source'])
        if handler is None:
            # We have no handler for this type of payload, simply ignore it
            return False
        else:
            handler(item)
            return True

    # Payload handlers with a generic interface: each takes the opaque payload
    # dict, unpacks it and calls the underlying functions with the necessary
    # arguments.

    def _handle_payload_page(self, item):
        data = item['data']
        text = data.get('text/plain', '')
        html = data.get('text/html', '')
        self.please_process.emit(PageDoc(text=text, html=html))

    def _handle_payload_edit(self, item):
        self.please_process.emit(EditFile(item['filename'], item['line_number']))

    def _handle_payload_exit(self, item):
        keep_kernel_on_exit = True if item['keepkernel'] else False
        self.please_process.emit(ExitRequested(keep_kernel_on_exit))

    def _handle_payload_next_input(self, item):
        self.please_process.emit(InText(item['text']))
