from functools import singledispatch
from subprocess import Popen

from qtconsole.qt import QtGui, QtCore
from qtconsole.util import MetaQObjectHasTraits
from traitlets import Integer, Unicode, Bool
from traitlets.config.configurable import LoggingConfigurable

from chconsole.entry import entry_template, LinePrompt
from chconsole.media import default_editor
from chconsole.messages import Exit, Execute, ClearAll, History, KernelMessage, ClearCurrentEntry
from chconsole.messages import ExportItem, UserInput
from chconsole.messages import PageDoc, InText, CompleteItems, CallTip, ExitRequested, InputRequest, EditFile, SplitItem
from chconsole.messages import Stderr, Stdout
from chconsole.messages import UserJoin, UserLeave
from chconsole.pager import pager_template
from chconsole.receiver import receiver_template
from chconsole.standards import NoDefaultEditor, CommandError
from .user_tracker import UserTracker

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def get_member(obj, dotted, default=None):
    """
    Return member or member of a member of the object specified.
    :param obj: object to get member from.
    :param dotted: dotted string representing the member or member of a member.
    :param default: any object.
    :return: whatever the method returns or default if non-existent.
    """
    if dotted:
        parts = dotted.split('.')
        sub_objects = parts[:-1]
        for p in sub_objects:
            if obj:
                obj = getattr(obj, p, None)
            else:
                break
        if obj:
            cmd = parts[len(parts)-1]
            member = getattr(obj, cmd, None)
            return member
    return default


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


# Receiver
@singledispatch
def _post(item, target):
    target.receiver.post(item)


# User
@_post.register(UserJoin)
def _(item, target):
    print(item.username + ' joined')
    target.user_tracker.insert(item.username, item.unique_id)
    print(target.user_tracker.users)


@_post.register(UserLeave)
def _(item, target):
    # print(item.username + ' left')
    target.user_tracker.remove(item.username, item.unique_id)
    # print(target.user_tracker.users)


# Pager
@_post.register(PageDoc)
def _(item, target):
    if target.receiver.covers(item):
        target.pager.post(item)
    else:
        target.receiver.post(item)


# Entry
@_post.register(InText)
@_post.register(CompleteItems)
@_post.register(CallTip)
@_post.register(ClearCurrentEntry)
def _(item, target):
    target.entry.post(item)


# Process here
@_post.register(ExitRequested)
def _(item, target):
    reply = QtGui.QMessageBox.Yes
    if item.confirm:
        title = target.window().windowTitle()
        reply = QtGui.QMessageBox.question(target, title,
                        "Kernel has been shutdown permanently. "
                        "Close the Console?",
                        QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
    if reply == QtGui.QMessageBox.Yes:
        target.please_export.emit(Exit(item.keep_kernel_on_exit))


@_post.register(EditFile)
def _(item, target):
    try:
        target.external_edit(item.filename, item.line_number)
    except NoDefaultEditor:
        text = ('No default editor available. '
                'Specify a GUI text editor in the `TabContent.editor` configurable '
                'to enable the %edit magic')
        target.receiver.post(Stderr(text))
    except KeyError:
        text = 'Invalid editor command.'
        target.receiver.post(Stderr(text))
    except CommandError as e:
        text = 'Opening editor with command "%s" failed.' % e.command
        target.receiver.post(Stderr(text))


@_post.register(InputRequest)
def _(item, target):
    target.entry.set_read_only(True)
    target.line_prompt.setParent(target.entry.current_widget)
    target.line_prompt.clear()
    target.line_prompt.prompt = item.prompt
    target.line_prompt.password = item.password
    target.line_prompt.setEnabled(True)
    target.line_prompt.set_focus()
    target.line_prompt.show()


@_post.register(ClearAll)
def _(item, target):
    target.clear_all()


@_post.register(History)
def _(item, target):
    items = []
    last_cell = u""
    for _, _, cell in item.items:
        cell = cell.rstrip()
        if cell != last_cell:
            items.append(cell)
            last_cell = cell
    target.history.set_history(items)


def tab_content_template(edit_class):
    """
    Template for TabWidget.
    :param edit_class: QTGui.QTextEdit or QtGui.QPlainTextEdit
    :return: Instantiated class.
    """
    class TabContent(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, QtGui.QSplitter), {})):
        entry_proportion = Integer(8, config=True,
                                   help="""
        1/entry_size is the height of the whole console to height of the command entry field.
        """)
        ansi_codes = Bool(True, config=True, help="Whether to process ANSI escape codes.")
        clear_on_kernel_restart = Bool(True, config=True,
            help="Whether to clear the console when the kernel is restarted")

        default_pager_location = Unicode('inside', config=True,
                                         help='Default location of the pager: right, inside or top')

        receiver = None  # Area of the console where chat messages, commands and outputs are shown
        entry = None  # Area of the console to enter commands and chat

        pager = None  # Pager object
        _pager_targets = {}  # Dictionary of target widgets where the pager can reside; see Pager

        _console_stack = None  # QWidget
        _console_stack_layout = None  # QStackedLayout
        _console_area = None  # QSplitter

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

        editor = Unicode(default_editor, config=False,
            help="""
            A command for invoking a system text editor. If the string contains a
            {filename} format specifier, it will be used. Otherwise, the filename
            will be appended to the end of the command.
            """)

        editor_line = Unicode(config=True,
            help="""
            The editor command to use when a specific line number is requested. The
            string should contain two format specifiers: {line} and {filename}. If
            this parameter is not specified, the line number option to the %edit
            magic will be ignored.
            """)

        please_export = QtCore.Signal(ExportItem)  # tasks for the kernel

        line_prompt = None  # LinePrompt for entering input requested by the kernel
        history = None  # History

        show_users = Bool(False, help='Whether to show the users in command input and output listings')
        user_tracker = None  # UserTracker for tracking users

        def __init__(self, is_complete, editor=default_editor, **kwargs):
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
            # receiver  |      pager_right
            #           | pager_inside
            # entry     |

            self.editor = editor

            self._console_stack = QtGui.QWidget()
            self._console_stack_layout = QtGui.QStackedLayout()
            self._console_stack.setLayout(self._console_stack_layout)
            self.addWidget(self._console_stack)

            self._console_area = QtGui.QSplitter(QtCore.Qt.Vertical)
            self._console_stack_layout.addWidget(self._console_area)

            self.entry = entry_template(edit_class)(is_complete=is_complete, use_ansi=self.ansi_codes)
            self.entry.please_export.connect(self.please_export)
            self.history = self.entry.history

            self.receiver = receiver_template(edit_class)(use_ansi=self.ansi_codes, show_users=self.show_users)
            self.receiver.please_export.connect(self.please_export)

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
                                                    'This is the pager!', use_ansi=self.ansi_codes)
            self.pager.hide()

            self.pager.release_focus.connect(self.entry.set_focus)
            self.receiver.release_focus.connect(self.entry.set_focus)
            self.entry.release_focus.connect(self.receiver.set_focus)

            self.line_prompt = LinePrompt()
            self.line_prompt.text_input.connect(self.on_text_input)

            self.show_users = self.receiver.text_register.get_visible()
            self.user_tracker = UserTracker()

        def _show_users_changed(self):
            self.receiver.text_register.set_visible(self.show_users)

        def clear_all(self):
            """
            Clear all widgets.
            :return:
            """
            self.entry.clear()
            self.receiver.clear()
            self.pager.clear()

        @property
        def _focus_text_component(self):
            """
            Text component widget that has focus; none if there is no focus on the text components.
            :return:
            """
            if self.pager.hasFocus():
                return self.pager
            elif self.receiver.hasFocus():
                return self.receiver
            elif self.entry.hasFocus():
                return self.entry
            else:
                return None

        def call_focus_method(self, dotted):
            """
            Execute method of the widget with focus if there is focus and the method exists;
            otherwise do nothing.
            :param dotted: dotted string representing the method None->None to be executed.
            :return: whatever the method returns.
            """
            focus_method = get_member(self._focus_text_component, dotted)
            if focus_method:
                return focus_method()
            else:
                return None

        # JupyterWidget
        def external_edit(self, filename, line=None):
            """ Opens an external editor.

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

        @QtCore.Slot(SplitItem)
        def post(self, item):
            _post(item, self)

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
        def on_enter_clicked(self):
            """
            After the user clicks enter, emit the source to be executed.
            :return:
            """
            source = self.entry.source
            self.post(ClearCurrentEntry())
            self.please_export.emit(Execute(source))

        @QtCore.Slot()
        def on_frontend_clicked(self):
            """
            After the user clicks message to frontend, emit the source to be sent to the receiver.
            :return:
            """
            # print('Send clicked')
            self._importer.convert(KernelMessage(eval(self.entry.source.code), from_here=True))

        @QtCore.Slot(str)
        def on_text_input(self, text):
            self.line_prompt.setEnabled(False)
            self.line_prompt.hide()
            self.please_export.emit(UserInput(text))
            if self.line_prompt.password:
                text = '****'
            out = self.line_prompt.prompt + text +'\n'
            self.post(Stdout(out))
            self.entry.set_focus()
            self.entry.set_read_only(False)

    return TabContent
