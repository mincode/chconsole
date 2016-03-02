import sys
from subprocess import Popen
from qtconsole.qt import QtGui, QtCore
from qtconsole.util import MetaQObjectHasTraits
from traitlets import Integer, Unicode, Bool
from traitlets.config.configurable import LoggingConfigurable
from dispatch.message import KernelMessage, Message
from dispatch.relay import Relay
from dispatch.source import Source
from dispatch.relay_item import RelayItem, PageDoc, EditFile, Stream, ExitRequested, InText, CompleteItems
from .entry import entry_template
from .pager import pager_template
from .receiver import receiver_template

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def _resize_last(splitter, fraction=4):
    """
    Resize the splitter making the last widget in it 1/fraction the height of it, and the preceding
    widgets share the remaining space equally.
    :param splitter: QSplitter to be resized.
    :param fraction: Integer.
    :return:
    """
    sizes = splitter.sizes()
    total_height = sum(sizes)
    num_widgets = len(sizes)
    height_last = total_height // fraction
    height_rest = (total_height * (fraction - 1)) // fraction
    new_sizes = [height_rest for i in range(num_widgets - 1)]
    new_sizes.append(height_last)
    splitter.setSizes(new_sizes)


# JupyterWidget
if sys.platform.startswith('win'):
    default_editor = 'notepad'
else:
    default_editor = ''


class NoDefaultEditor(Exception):
    def __init__(self):
        super(NoDefaultEditor, self).__init__()

    def __str__(self):
        return 'NoDefaultEditor'


class CommandError(Exception):
    command = ''

    def __init__(self, command):
        super(CommandError, self).__init__()
        self.command = command


def tab_content_template(edit_class):
    """
    Template for TabWidget.
    :param edit_class: QTGui.QTextEdit or QtGui.QPlainTextEdit
    :return: Instantiated class.
    """
    class TabContent(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, QtGui.QSplitter), {})):
        entry_proportion = Integer(5, config=True,
                                   help="""
        1/entry_size is the height of the whole console to height of the command entry field.
        """)
        ansi_codes = Bool(True, config=True, help="Whether to process ANSI escape codes.")

        default_pager_location = Unicode('right', config=True, help='Default location of the pager: right, inside or top')

        receiver = None  # Area of the console where chat messages, commands and outputs are shown
        entry = None  # Area of the console to enter commands and chat

        pager = None  # Pager object
        _pager_targets = {}  # Dictionary of target widgets where the pager can reside; see Pager

        _console_stack = None  # QWidget
        _console_stack_layout = None  # QStackedLayout
        _console_area = None  # QSplitter

        _relay = None  # Relay

        show_other = Bool(True, config=True, help='True if messages from other clients are to be included.')

        message_arrived = QtCore.Signal(Message)  # to signal a message from the kernel
        please_execute = QtCore.Signal(Source)  # source to be executed

        print_action = None  # action for printing
        export_action = None # action for exporting
        select_all_action = None  # action for selecting all
        increase_font_size = None  # action for increasing font size
        decrease_font_size = None  # action for decreasing font size
        reset_font_size = None  # action for resetting font size

        # JupyterWidget:
        # If set, the 'custom_edit_requested(str, int)' signal will be emitted when
        # an editor is needed for a file. This overrides 'editor' and 'editor_line'
        # settings.
        custom_edit = Bool(False)
        custom_edit_requested = QtCore.Signal(object, object)

        editor = Unicode(default_editor, config=True,
            help="""
            A command for invoking a system text editor. If the string contains a
            {filename} format specifier, it will be used. Otherwise, the filename
            will be appended to the end the command.
            """)

        editor_line = Unicode(config=True,
            help="""
            The editor command to use when a specific line number is requested. The
            string should contain two format specifiers: {line} and {filename}. If
            this parameter is not specified, the line number option to the %edit
            magic will be ignored.
            """)

        # Signal when exit is requested
        please_exit = QtCore.Signal(bool)

        # Signal requesting completing code str ad cursor position int.
        please_complete = QtCore.Signal(str, int)

        def __init__(self, is_complete, **kwargs):
            """
            Initialize
            :param is_complete: function str->(bool, str) that checks whether the input is complete code
            :param kwargs: arguments for LoggingConfigurable
            :return:
            """
            QtGui.QSplitter.__init__(self, QtCore.Qt.Horizontal)
            LoggingConfigurable.__init__(self, **kwargs)
            # Layout overview:
            # pager_top
            # view  |      pager_right
            #       | pager_inside
            # entry |

            self._console_stack = QtGui.QWidget()
            self._console_stack_layout = QtGui.QStackedLayout()
            self._console_stack.setLayout(self._console_stack_layout)
            self.addWidget(self._console_stack)

            self._console_area = QtGui.QSplitter(QtCore.Qt.Vertical)
            self._console_stack_layout.addWidget(self._console_area)

            self.entry = entry_template(edit_class)(is_complete=is_complete)
            self.entry.please_execute.connect(self.on_send_clicked)
            self.entry.please_complete.connect(self.please_complete)
            self.receiver = receiver_template(edit_class)()
            self._console_area.addWidget(self.receiver)
            self._console_area.addWidget(self.entry)

            self.print_action = self.receiver.print_action
            self.export_action = self.receiver.export_action
            self.select_all_action = self.receiver.select_all_action
            self.increase_font_size = self.receiver.increase_font_size
            self.decrease_font_size = self.receiver.decrease_font_size
            self.reset_font_size = self.receiver.reset_font_size

            self._pager_targets = [
                ('right', {'target': self, 'index': 1}),
                ('top', {'target': self._console_area, 'index': 0}),
                ('inside', {'target': self._console_stack_layout, 'index': 1})
            ]

            self.pager = pager_template(edit_class)(self._pager_targets, self.default_pager_location,
                                                    'This is the pager!')
            self.pager.hide()

            self._relay = Relay(self)
            self._relay.please_process.connect(self.post)
            self.message_arrived.connect(self._relay.dispatch)

            self.pager.release_focus.connect(self.entry.set_focus)
            self.receiver.release_focus.connect(self.entry.set_focus)

        def clear(self):
            self.receiver.clear()

        # JupyterWidget
        def _edit(self, filename, line=None):
            """ Opens a Python script for editing.

            Parameters
            ----------
            filename : str
                A path to a local system file.

            line : int, optional
                A line of interest in the file.
            """
            if self.custom_edit:
                self.custom_edit_requested.emit(filename, line)
            elif not self.editor:
                raise NoDefaultEditor()
            else:
                try:
                    filename = '"%s"' % filename
                    if line and self.editor_line:
                        command = self.editor_line.format(filename=filename,
                                                          line=line)
                    else:
                        try:
                            command = self.editor.format()
                        except KeyError:
                            command = self.editor.format(filename=filename)
                        else:
                            command += ' ' + filename
                except KeyError:
                    raise
                else:
                    try:
                        Popen(command, shell=True)
                    except OSError:
                        raise CommandError(command)

        @QtCore.Slot(RelayItem)
        def post(self, item):
            # To external
            if isinstance(item, ExitRequested):
                self.please_exit.emit(item.keep_kernel_on_exit)
            # Pager
            elif isinstance(item, PageDoc) and self.receiver.covers(item):
                self.pager.post(item)
            # Entry
            elif isinstance(item, InText):
                self.entry.post(item)
            elif isinstance(item, CompleteItems):
                self.entry.post(item)
            # Receiver
            elif isinstance(item, EditFile):
                try:
                    self._edit(item.filename, item.line_number)
                except NoDefaultEditor:
                    text = ('No default editor available. '
                            'Specify a GUI text editor in the `TabContent.editor` configurable '
                            'to enable the %edit magic')
                    self.receiver.post(Stream(text=text, name='stderr', clearable=False))
                except KeyError:
                    text = 'Invalid editor command.'
                    self.receiver.post(Stream(text=text, name='stderr', clearable=False))
                except CommandError as e:
                    text = 'Opening editor with command "%s" failed.' % e.command
                    self.receiver.post(Stream(text=text, name='stderr', clearable=False))
            else:
                self.receiver.post(item)

        @property
        def pager_locations(self):
            """
            Available pager locations.
            :return: List of strings representing the available pager locations.
            """
            return [t[0] for t in self._pager_targets]

        # Qt events
        def showEvent(self, event):
            if not event.spontaneous():
                _resize_last(self._console_area, self.entry_proportion)

        # Qt slots
        @QtCore.Slot()
        def on_send_clicked(self):
            """
            After the user clicks send, emit the source to be executed.
            :return:
            """
            # print('Send clicked')
            self.please_execute.emit(self.entry.source)

        @QtCore.Slot()
        def on_frontend_clicked(self):
            """
            After the user clicks message to frontend, emit the source to be sent to the receiver.
            :return:
            """
            # print('Send clicked')
            self.dispatch(Message(eval(self.entry.source.code), from_here=True))

        @QtCore.Slot(KernelMessage)
        def dispatch(self, msg):
            msg = Message(msg)
            msg.show_other = self.show_other
            msg.ansi_codes = self.ansi_codes
            self.message_arrived.emit(msg)

    return TabContent
