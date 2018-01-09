import time
from base64 import decodebytes

from qtconsole.qt import QtCore
from qtconsole.util import MetaQObjectHasTraits
from traitlets.config.configurable import LoggingConfigurable

from chconsole.messages import (CompleteItems, PageDoc,
                                EditFile, InText, CallTip,
                                InputRequest, ExportItem,
                                TailHistory, History)
from chconsole.messages import (ImportItem, Stderr, Stdout,
                                Banner, HtmlText, ExitRequested,
                                Input, Result, ClearOutput)
from chconsole.messages import SvgXml, Png, Jpeg, LaTeX
from chconsole.messages import filter_meta_command, AddUser
from chconsole.standards import Importable
from traitlets import Bool

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def _show_msg(msg, show_other):
    """
    Determine if message should be shown.
    :param msg: message to be shown.
    :param show_other: whether messages from other clients should be shown.
    :return: whether the message should be shown.
    """
    return msg.from_here or show_other


class Importer(MetaQObjectHasTraits('NewBase', (LoggingConfigurable,
                                                QtCore.QObject), {})):
    """
    Import messages into objects handled by the ui.
    """
    please_process = QtCore.Signal(ImportItem)
    please_export = QtCore.Signal(ExportItem)  # tasks for the kernel

    _payload_source_edit = 'edit_magic'
    _payload_source_exit = 'ask_exit'
    _payload_source_next_input = 'set_next_input'
    _payload_source_page = 'page'

    target = None  # parent object

    _retry_history = None  # QSemaphore(1) allows one retry of a history request

    client_id = ''  # unique id string for this client instance
    user_name = ''  # user name
    chat_secret = ''  # secret id for chat communication
    show_arriving_msg = Bool(False, config=True,
                    help='whether to show messages as they arrive; for debugging')

    def __init__(self, parent=None, chat_secret='',
                 client_id='', user_name='', **kwargs):
        """
        Initialize.
        :param client_id: unique id for this client instance
        :param parent: parent object, requires data member show_other.
        :param kwargs:
        :return:
        """
        QtCore.QObject.__init__(self, parent)
        LoggingConfigurable.__init__(self, **kwargs)
        self.chat_secret = chat_secret
        self.client_id = client_id
        self.user_name = user_name
        self.target = parent
        self._retry_history = QtCore.QSemaphore(1)

        self._payload_handlers = {
            self._payload_source_edit: self._handle_payload_edit,
            self._payload_source_exit: self._handle_payload_exit,
            self._payload_source_page: self._handle_payload_page,
            self._payload_source_next_input: self._handle_payload_next_input}

    @QtCore.Slot(Importable)
    def convert(self, msg):
        if self.show_arriving_msg:
            print('\nconvert: ' + msg.type + ', user: ' + msg.username)
        if isinstance(msg, ImportItem):
            self.please_process.emit(msg)
        else:  # KernelMessage
            if self.show_arriving_msg:
                print(msg.raw)
            handler = getattr(self, '_handle_' + msg.type, None)
            if handler and _show_msg(msg, self.target.show_other):
                handler(msg)

    def _handle_stream(self, msg):
        content = msg.content
        name = content['name']
        if name == 'stderr':
            self.please_process.emit(Stderr(content['text'], username=msg.username))
        else:
            self.please_process.emit(Stdout(content['text'], username=msg.username))

    def _handle_kernel_info_reply(self, msg):
        """
        Kernel info reply banner on startup.
        :param msg:
        :return:
        """
        to_show = msg.content['banner']
        help_links = msg.content['help_links']
        banner = Banner(to_show, help_links=help_links.copy(), username=msg.username)
        self.please_process.emit(banner)

    # FrontendWidget
    def _kernel_restarted(self, msg):
        """
        Notice kernel has been restarted.
        :param msg: message that is associated with the restart.
        :return:
        """
        self.log.warn("kernel restarted")
        notice = "Kernel has been started."
        html_text = "<br>%s<hr><br>" % notice
        self.please_process.emit(Stderr(HtmlText(html_text, username=msg.username), username=msg.username))

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
                self._kernel_restarted(msg)
            else:
                # kernel was shutdown permanently
                # this triggers exit_requested if the kernel was local,
                # and a dialog if the kernel was remote,
                # so we don't suddenly clear the console without asking.
                self.please_process.emit(ExitRequested(False, confirm=not msg.local_kernel, username=msg.username))

    # FrontendWidget
    def _handle_status(self, msg):
        """Handle status message"""
        # This is where a busy/idle indicator would be triggered,
        # when we make one.
        state = msg.content.get('execution_state', '')
        if state == 'starting':
            self._kernel_restarted(msg)
        elif state == 'idle':
            pass
        elif state == 'busy':
            pass

    # JupyterWidget
    def _handle_history_reply(self, msg):
        """ Implemented to handle history tail replies, which are only supported
            by Jupyter kernels.
        """
        content = msg.content
        if 'history' not in content:
            self.log.error("History request failed: %r"%content)
            if content.get('status', '') == 'aborted':
                if self._retry_history.tryAcquire():
                    # a *different* action caused this request to be aborted, so
                    # we should try again.
                    self.log.error("Retrying aborted history request")
                    # wait out the kernel's queue flush, which is currently timed at 0.1s
                    time.sleep(0.25)
                    self.please_export.emit(TailHistory(1000, username=msg.username))
                else:
                    self._retry_history.release()
        else:
            if not self._retry_history.tryAcquire():
                # history received from a retry
                self._retry_history.release()

            history_items = content['history']
            self.log.debug("Received history reply with %i entries", len(history_items))
            self.please_process.emit(History(history_items, username=msg.username))
            # Since the client sends a history request upon connecting, we send an add user for any received history
            # request, to register the user.
            # self.please_export.emit(AddUser(self.chat_secret, self.client_id, self.user_name))
            # since it is lost occasionally, send twice
            # self.please_export.emit(AddUser(self.chat_secret, self.client_id, self.user_name))
            # self.please_export.emit(WhoUser(self.chat_secret, self.client_id, self.user_name))

    def _handle_execute_input(self, msg):
        """Handle an execute_input message"""
        content = msg.content
        self.log.debug("execute_input: %s", content)

        meta_command = filter_meta_command(self.chat_secret, content['code'])
        if meta_command:
            # print("COMMAND META")
            # Use AddUser only if it goes to the current client
            if not isinstance(meta_command, AddUser) or meta_command.to(self.client_id, self.user_name):
                to_process = meta_command
            else:
                to_process = None
            to_process = meta_command
        else:
            to_process = Input(content['code'], execution_count=content['execution_count'],
                               username=msg.parent_username)
        if to_process:
            self.please_process.emit(to_process)

    def _handle_display_data(self, msg):
        data = msg.content['data']
        metadata = msg.content.get('metadata', None)
        if 'image/svg+xml' in data:
            self.please_process.emit(SvgXml(data['image/svg+xml'], username=msg.username))
        elif 'image/png' in data:
            img = decodebytes(data['image/png'].encode('ascii'))
            self.please_process.emit(Png(img, metadata=metadata.get('image/png', None), username=msg.username))
        elif 'image/jpeg' in data:
            img = decodebytes(data['image/jpeg'].encode('ascii'))
            self.please_process.emit(Jpeg(img, metadata=metadata.get('image/jpeg', None), username=msg.username))
        elif 'text/latex' in data:
            self.please_process.emit(LaTeX(data['text/latex'], username=msg.username))
        elif 'text/plain' in data:
            self.please_process.emit(Stdout(data['text/plain'], username=msg.username))

        # to test:
        # import matplotlib.pyplot as plt
        # plt.plot([1, 2, 3, 4])
        # plt.ylabel('some nums')
        # plt.show()

    def _handle_execute_result(self, msg):
        """Handle an execute_result message"""
        prompt_number = msg.content.get('execution_count', 0)
        data = msg.content['data']
        metadata = msg.content.get('metadata', None)

        result = Result(data.get('text/plain', None), execution_count=prompt_number, username=msg.username)

        if 'image/svg+xml' in data:
            result.content.append(SvgXml(data['image/svg+xml'], username=msg.username))
        elif 'image/png' in data:
            img = decodebytes(data['image/png'].encode('ascii'))
            result.content.append(Png(img, metadata=metadata.get('image/png', None), username=msg.username))
        elif 'image/jpeg' in data:
            img = decodebytes(data['image/jpeg'].encode('ascii'))
            result.content.append(Jpeg(img, metadata=metadata.get('image/jpeg', None), username=msg.username))
        elif 'text/latex' in data:
            result.content.append(LaTeX(data['text/latex'], username=msg.username))

        self.please_process.emit(result)

    def _handle_clear_output(self, msg):
        # {'header': {'msg_type': 'clear_output'}, 'content': {'wait': False}}
        #
        # {'header': {'msg_type': 'clear_output'}, 'content': {'wait': False}}
        # {'header': {'msg_type': 'stream'}, 'content': {'name': 'stdout', 'text': 'XYZ'}}
        content = msg.content
        # print('wait: ' + str(content['wait']))
        self.please_process.emit(ClearOutput(wait=content['wait'], username=msg.username))

    def _handle_complete_reply(self, msg):
        self.log.debug("complete: %s", msg.content)
        if msg.from_here:
            matches = msg.content['matches']
            start = msg.content['cursor_start']
            end = msg.content['cursor_end']
            self.please_process.emit(CompleteItems(matches=matches, start=start, end=end, username=msg.username))

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
            if not self._process_execute_payload(item, msg.username):
                warning = 'Warning: received unknown payload of type %s'
                print(warning % repr(item['source']))

    # JupyterWidget
    def _process_execute_payload(self, item, username):
        """ Reimplemented to dispatch payloads to handler methods.
        """
        handler = self._payload_handlers.get(item['source'])
        if handler is None:
            # We have no handler for this type of payload, simply ignore it
            return False
        else:
            handler(item, username)
            return True

    # Payload handlers with a generic interface: each takes the opaque payload
    # dict, unpacks it and calls the underlying functions with the necessary
    # arguments.

    def _handle_payload_page(self, item, username):
        print('payload page message')
        data = item['data']
        text = data.get('text/plain', '')
        print(text)
        html = data.get('text/html', '')
        self.please_process.emit(PageDoc(text=text, html=html, username=username))

    def _handle_payload_edit(self, item, username):
        self.please_process.emit(EditFile(item['filename'], item['line_number'], username=username))

    def _handle_payload_exit(self, item, username):
        keep_kernel_on_exit = True if item['keepkernel'] else False
        self.please_process.emit(ExitRequested(keep_kernel_on_exit, username=username))

    def _handle_payload_next_input(self, item, username):
        self.please_process.emit(InText(item['text'], username=username))

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

            ename = msg.content['ename']
            ename_styled = '<span class="error">%s</span>' % ename
            traceback = traceback.replace(ename, ename_styled)

            # self._append_html(traceback)
            # post traceback as html
        else:
            # This is the fallback for now, using plain text with ansi escapes
            self.please_process.emit(Stderr(traceback, username=msg.username))

    # FrontendWidget
    def _process_execute_abort(self, msg):
        """ Process a reply for an aborted execution request.
        """
        self.please_process.emit(Stderr('ERROR: execution aborted', username=msg.username))

    # FrontendWidget
    def _handle_inspect_reply(self, msg):
        """Handle replies for call tips."""
        self.log.debug("info: %s", msg.content)
        if msg.from_here and msg.content.get('status') == 'ok' and msg.content.get('found', False):
            self.please_process.emit(CallTip(msg.content, username=msg.username))

    def _handle_input_request(self, msg):
        self.please_process.emit(InputRequest(msg.content.get('prompt', ''), msg.content.get('password', False),
                                              username=msg.username))
