from qtconsole.qt import QtCore
from qtconsole.util import MetaQObjectHasTraits
from traitlets.config.configurable import LoggingConfigurable

from messages.import_item import ImportItem, Stderr, Stdout, Banner, HtmlText, ExitRequested, Input, Result, ClearOutput, \
    CompleteItems, PageDoc, EditFile, InText, CallTip, InputRequest

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def _show_msg(msg, show_other):
    """
    Determine if message should be shown.
    :param msg: message to be shown.
    :param show_other: whether messages from other clients should be shown.
    :return: whether the message should be shown.
    """
    return msg.from_here or show_other


class Importer(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, QtCore.QObject), {})):
    """
    Import messages into objects handled by the ui.
    """
    please_process = QtCore.Signal(ImportItem)

    _payload_source_edit = 'edit_magic'
    _payload_source_exit = 'ask_exit'
    _payload_source_next_input = 'set_next_input'
    _payload_source_page = 'page'

    def __init__(self, parent=None, **kwargs):
        QtCore.QObject.__init__(self, parent)
        LoggingConfigurable.__init__(self, **kwargs)

        self._payload_handlers = {
            self._payload_source_edit: self._handle_payload_edit,
            self._payload_source_exit: self._handle_payload_exit,
            self._payload_source_page: self._handle_payload_page,
            self._payload_source_next_input: self._handle_payload_next_input}

    def convert(self, msg, show_other=True):
        print('dispatch: ' + msg.type)
        print(msg.raw)
        handler = getattr(self, '_handle_' + msg.type, None)
        if handler and _show_msg(msg, show_other):
            handler(msg)

    def _handle_stream(self, msg):
        content = msg.content
        name = content['name']
        if name == 'stderr':
            self.please_process.emit(Stderr(content['text']))
        else:
            self.please_process.emit(Stdout(content['text']))

    def _handle_kernel_info_reply(self, msg):
        to_show = msg.content['banner']
        help_links = msg.content['help_links']
        banner = Banner(to_show, help_links=help_links.copy())
        self.please_process.emit(banner)

    # FrontendWidget
    def _kernel_restarted(self, died=True):
        """Notice that the autorestarter restarted the kernel.
        There's nothing to do but show a message.
        """
        self.log.warn("kernel restarted")
        msg = "Kernel died, restarting" if died else "Kernel restarting"
        text = "<br>%s<hr><br>" % msg
        self.please_process.emit(Stderr(HtmlText(text)))

    # FrontendWidget
    def _handle_shutdown_reply(self, msg):
        """ Handle shutdown signal, only if from other console.
        """
        self.log.debug("shutdown: %s", msg.content)
        restart = msg.content.get('restart', False)
        if not msg.from_here:
            # got shutdown reply, request came from session other than ours
            if restart:
                # someone restarted the kernel, handle it
                self._kernel_restarted(died=False)
            else:
                # kernel was shutdown permanently
                # this triggers exit_requested if the kernel was local,
                # and a dialog if the kernel was remote,
                # so we don't suddenly clear the console without asking.
                self.please_process.emit(ExitRequested(False, confirm=not msg.local_kernel))

    def _handle_status(self, msg):
        """Handle status message"""
        # This is where a busy/idle indicator would be triggered,
        # when we make one.
        state = msg.content.get('execution_state', '')
        if state == 'starting':
            self._kernel_restarted(died=True)
        elif state == 'idle':
            pass
        elif state == 'busy':
            pass

    # def _handle_history_reply(self, msg):
    #     print('history reply dropped')

    def _handle_execute_input(self, msg):
        """Handle an execute_input message"""
        content = msg.content
        self.log.debug("execute_input: %s", content)

        self.please_process.emit(Input(content['code'], execution_count=content['execution_count']))

    def _handle_execute_result(self, msg):
        """Handle an execute_result message"""
        content = msg.content
        prompt_number = content.get('execution_count', 0)
        data = content['data']
        if 'text/plain' in data:
            self.please_process.emit(Result(data['text/plain'], execution_count=prompt_number))

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
            self.please_process.emit(Stdout(data['text/plain']))

    def _handle_complete_reply(self, msg):
        self.log.debug("complete: %s", msg.content)
        if msg.from_here:
            matches = msg.content['matches']
            start = msg.content['cursor_start']
            end = msg.content['cursor_end']
            self.please_process.emit(CompleteItems(matches=matches, start=start, end=end))

    # frontend_widget
    def _handle_execute_reply(self, msg):
        self.log.debug("execute: %s", msg.content)
        status = msg.content['status']
        if status == 'ok':
            self._process_execute_ok(msg)
        elif status == 'error':
            self._process_execute_error(msg)
        elif status == 'aborted':
            self._process_execute_abort(msg)
        # MM: FrontendWidget also has an option for 'silent_exec_callback' which does not seem to be used
        # Therefore it is not implemented here.
        # JupyterWidget also handles prompt requests, to show the current prompt in the input area. Since we
        # are not using prompts, this is not implemented.

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
        print('payload page message')
        data = item['data']
        text = data.get('text/plain', '')
        print(text)
        html = data.get('text/html', '')
        self.please_process.emit(PageDoc(text=text, html=html))

    def _handle_payload_edit(self, item):
        self.please_process.emit(EditFile(item['filename'], item['line_number']))

    def _handle_payload_exit(self, item):
        keep_kernel_on_exit = True if item['keepkernel'] else False
        self.please_process.emit(ExitRequested(keep_kernel_on_exit))

    def _handle_payload_next_input(self, item):
        self.please_process.emit(InText(item['text']))

    # JupyterWidget
    def _process_execute_error(self, msg):
        """Handle an execute_error message"""
        traceback = '\n'.join(msg.content['traceback']) + '\n'
        if False:
            # For now, tracebacks come as plain text, so we can't use
            # the html renderer yet.  Once we refactor ultratb to produce
            # properly styled tracebacks, this branch should be the default
            traceback = traceback.replace(' ', '&nbsp;')
            traceback = traceback.replace('\n', '<br/>')

            ename = content['ename']
            ename_styled = '<span class="error">%s</span>' % ename
            traceback = traceback.replace(ename, ename_styled)

            # self._append_html(traceback)
            # post traceback as html
        else:
            # This is the fallback for now, using plain text with ansi escapes
            self.please_process.emit(Stderr(traceback))

    # FrontendWidget
    def _process_execute_abort(self, msg):
        """ Process a reply for an aborted execution request.
        """
        self.please_process.emit(Stderr('ERROR: execution aborted'))

    # FrontendWidget
    def _handle_inspect_reply(self, msg):
        """Handle replies for call tips."""
        self.log.debug("info: %s", msg.content)
        if msg.from_here and msg.content.get('status') == 'ok' and msg.content.get('found', False):
            self.please_process.emit(CallTip(msg.content))

    def _handle_input_request(self, msg):
        self.please_process.emit(InputRequest(msg.content.get('prompt', ''), msg.content.get('password', False)))