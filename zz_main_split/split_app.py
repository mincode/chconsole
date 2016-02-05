from qtconsole.qt import QtCore, QtGui

from qtconsole.jupyter_widget import JupyterWidget
from qtconsole.rich_jupyter_widget import RichJupyterWidget

from qtconsole.qtconsoleapp import JupyterQtConsoleApp

from zz_main_split.signal_content import SignalContent, TextSignal, HtmlSignal

import qtconsole.qtconsoleapp
import zz_main_split.split_main_window
qtconsole.qtconsoleapp.MainWindow = zz_main_split.split_main_window.MainWindow


def split_control(self):
    if self.kind == 'rich':
        control = QtGui.QTextEdit()
    else:
        control = QtGui.QPlainTextEdit()
    return control


def split_page_control(self):
    if self.kind == 'rich':
        control = QtGui.QTextEdit()
    else:
        control = QtGui.QPlainTextEdit()
    return control

# assign custom_control and custom_page_control for the widgets

#override _append_custom(self, insert, input, before_prompt=False, *args, **kwargs):
#ovverride JupyterWidget._handle_execute_result


class _Signaller(QtCore.QObject):
    message_ready = QtCore.Signal(SignalContent)

    def __init__(self):
        super().__init__()
        # self.message_ready = pyqtSignal(SignalContent) does not work/incorrect?

    def connect_signal(self, slot_fun):
        self.message_ready.connect(slot_fun)

    def emit_signal(self, record):
        self.message_ready.emit(record)


class RichChatWidget(RichJupyterWidget):
    signaller = None

    def __init__(self, *args, **kwargs):
        super(RichChatWidget, self).__init__(*args, **kwargs)
        self.custom_control = split_control
        self.custom_page_control = split_page_control
        self.signaller = _Signaller()

    def _handle_execute_result(self, msg):
        """Handle an execute_result message"""
        if self.include_output(msg):
            self.flush_clearoutput()
            content = msg['content']
            prompt_number = content.get('execution_count', 0)
            data = content['data']
            if 'text/plain' in data:
                ###self._append_plain_text(self.output_sep, True)
                to_append = self.output_sep
                self.signaller.emit_signal(TextSignal(to_append))

                ###self._append_html(self._make_out_prompt(prompt_number), True)
                to_append = self._make_out_prompt(prompt_number)
                self.signaller.emit_signal(HtmlSignal(to_append))

                text = data['text/plain']
                # If the repr is multiline, make sure we start on a new line,
                # so that its lines are aligned.
                if "\n" in text and not self.output_sep.endswith("\n"):
                    ####self._append_plain_text('\n', True)
                    to_append = '\n'
                    self.signaller.emit_signal(TextSignal(to_append))

                ###self._append_plain_text(text + self.output_sep2, True)
                to_append = text + self.output_sep2
                # append in command_view
                self.signaller.emit_signal(TextSignal(to_append))
                self.signaller.emit_signal(TextSignal('\n'))

    def _event_filter_console_keypress(self, event):
        """ Filter key events for the underlying text widget to create a
            console-like interface.
        """
        intercepted = False
        cursor = self._control.textCursor()
        position = cursor.position()
        key = event.key()
        ctrl_down = self._control_key_down(event.modifiers())
        alt_down = event.modifiers() & QtCore.Qt.AltModifier
        shift_down = event.modifiers() & QtCore.Qt.ShiftModifier

        #------ Special sequences ----------------------------------------------

        if event.matches(QtGui.QKeySequence.Copy):
            self.copy()
            intercepted = True

        elif event.matches(QtGui.QKeySequence.Cut):
            self.cut()
            intercepted = True

        elif event.matches(QtGui.QKeySequence.Paste):
            self.paste()
            intercepted = True

        #------ Special modifier logic -----------------------------------------

        elif key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            intercepted = True

            # Special handling when tab completing in text mode.
            self._cancel_completion()

            if self._in_buffer(position):
                # Special handling when a reading a line of raw input.
                if self._reading:
                    #self._append_plain_text('\n')
                    ######################################################################################
                    cursor.insertText('\n')
                    ######################################################################################
                    self._reading = False
                    if self._reading_callback:
                        self._reading_callback()

                # If the input buffer is a single line or there is only
                # whitespace after the cursor, execute. Otherwise, split the
                # line with a continuation prompt.
                elif not self._executing:
                    cursor.movePosition(QtGui.QTextCursor.End,
                                        QtGui.QTextCursor.KeepAnchor)
                    at_end = len(cursor.selectedText().strip()) == 0
                    single_line = (self._get_end_cursor().blockNumber() ==
                                   self._get_prompt_cursor().blockNumber())
                    if (at_end or shift_down or single_line) and not ctrl_down:
                        self.execute(interactive = not shift_down)
                    else:
                        # Do this inside an edit block for clean undo/redo.
                        cursor.beginEditBlock()
                        cursor.setPosition(position)
                        cursor.insertText('\n')
                        self._insert_continuation_prompt(cursor)
                        cursor.endEditBlock()

                        # Ensure that the whole input buffer is visible.
                        # FIXME: This will not be usable if the input buffer is
                        # taller than the console widget.
                        self._control.moveCursor(QtGui.QTextCursor.End)
                        self._control.setTextCursor(cursor)

        #------ Control/Cmd modifier -------------------------------------------

        elif ctrl_down:
            if key == QtCore.Qt.Key_G:
                self._keyboard_quit()
                intercepted = True

            elif key == QtCore.Qt.Key_K:
                if self._in_buffer(position):
                    cursor.clearSelection()
                    cursor.movePosition(QtGui.QTextCursor.EndOfLine,
                                        QtGui.QTextCursor.KeepAnchor)
                    if not cursor.hasSelection():
                        # Line deletion (remove continuation prompt)
                        cursor.movePosition(QtGui.QTextCursor.NextBlock,
                                            QtGui.QTextCursor.KeepAnchor)
                        cursor.movePosition(QtGui.QTextCursor.Right,
                                            QtGui.QTextCursor.KeepAnchor,
                                            len(self._continuation_prompt))
                    self._kill_ring.kill_cursor(cursor)
                    self._set_cursor(cursor)
                intercepted = True

            elif key == QtCore.Qt.Key_L:
                self.prompt_to_top()
                intercepted = True

            elif key == QtCore.Qt.Key_O:
                if self._page_control and self._page_control.isVisible():
                    self._page_control.setFocus()
                intercepted = True

            elif key == QtCore.Qt.Key_U:
                if self._in_buffer(position):
                    cursor.clearSelection()
                    start_line = cursor.blockNumber()
                    if start_line == self._get_prompt_cursor().blockNumber():
                        offset = len(self._prompt)
                    else:
                        offset = len(self._continuation_prompt)
                    cursor.movePosition(QtGui.QTextCursor.StartOfBlock,
                                        QtGui.QTextCursor.KeepAnchor)
                    cursor.movePosition(QtGui.QTextCursor.Right,
                                        QtGui.QTextCursor.KeepAnchor, offset)
                    self._kill_ring.kill_cursor(cursor)
                    self._set_cursor(cursor)
                intercepted = True

            elif key == QtCore.Qt.Key_Y:
                self._keep_cursor_in_buffer()
                self._kill_ring.yank()
                intercepted = True

            elif key in (QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete):
                if key == QtCore.Qt.Key_Backspace:
                    cursor = self._get_word_start_cursor(position)
                else: # key == QtCore.Qt.Key_Delete
                    cursor = self._get_word_end_cursor(position)
                cursor.setPosition(position, QtGui.QTextCursor.KeepAnchor)
                self._kill_ring.kill_cursor(cursor)
                intercepted = True

            elif key == QtCore.Qt.Key_D:
                if len(self.input_buffer) == 0:
                    self.exit_requested.emit(self)
                else:
                    new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                                QtCore.Qt.Key_Delete,
                                                QtCore.Qt.NoModifier)
                    QtGui.qApp.sendEvent(self._control, new_event)
                    intercepted = True

        #------ Alt modifier ---------------------------------------------------

        elif alt_down:
            if key == QtCore.Qt.Key_B:
                self._set_cursor(self._get_word_start_cursor(position))
                intercepted = True

            elif key == QtCore.Qt.Key_F:
                self._set_cursor(self._get_word_end_cursor(position))
                intercepted = True

            elif key == QtCore.Qt.Key_Y:
                self._kill_ring.rotate()
                intercepted = True

            elif key == QtCore.Qt.Key_Backspace:
                cursor = self._get_word_start_cursor(position)
                cursor.setPosition(position, QtGui.QTextCursor.KeepAnchor)
                self._kill_ring.kill_cursor(cursor)
                intercepted = True

            elif key == QtCore.Qt.Key_D:
                cursor = self._get_word_end_cursor(position)
                cursor.setPosition(position, QtGui.QTextCursor.KeepAnchor)
                self._kill_ring.kill_cursor(cursor)
                intercepted = True

            elif key == QtCore.Qt.Key_Delete:
                intercepted = True

            elif key == QtCore.Qt.Key_Greater:
                self._control.moveCursor(QtGui.QTextCursor.End)
                intercepted = True

            elif key == QtCore.Qt.Key_Less:
                self._control.setTextCursor(self._get_prompt_cursor())
                intercepted = True

        #------ No modifiers ---------------------------------------------------

        else:
            if shift_down:
                anchormode = QtGui.QTextCursor.KeepAnchor
            else:
                anchormode = QtGui.QTextCursor.MoveAnchor

            if key == QtCore.Qt.Key_Escape:
                self._keyboard_quit()
                intercepted = True

            elif key == QtCore.Qt.Key_Up:
                if self._reading or not self._up_pressed(shift_down):
                    intercepted = True
                else:
                    prompt_line = self._get_prompt_cursor().blockNumber()
                    intercepted = cursor.blockNumber() <= prompt_line

            elif key == QtCore.Qt.Key_Down:
                if self._reading or not self._down_pressed(shift_down):
                    intercepted = True
                else:
                    end_line = self._get_end_cursor().blockNumber()
                    intercepted = cursor.blockNumber() == end_line

            elif key == QtCore.Qt.Key_Tab:
                if not self._reading:
                    if self._tab_pressed():
                        # real tab-key, insert four spaces
                        cursor.insertText(' '*4)
                    intercepted = True

            elif key == QtCore.Qt.Key_Left:

                # Move to the previous line
                line, col = cursor.blockNumber(), cursor.columnNumber()
                if line > self._get_prompt_cursor().blockNumber() and \
                        col == len(self._continuation_prompt):
                    self._control.moveCursor(QtGui.QTextCursor.PreviousBlock,
                                             mode=anchormode)
                    self._control.moveCursor(QtGui.QTextCursor.EndOfBlock,
                                             mode=anchormode)
                    intercepted = True

                # Regular left movement
                else:
                    intercepted = not self._in_buffer(position - 1)

            elif key == QtCore.Qt.Key_Right:
                original_block_number = cursor.blockNumber()
                self._control.moveCursor(QtGui.QTextCursor.Right,
                                mode=anchormode)
                if cursor.blockNumber() != original_block_number:
                    self._control.moveCursor(QtGui.QTextCursor.Right,
                                        n=len(self._continuation_prompt),
                                        mode=anchormode)
                intercepted = True

            elif key == QtCore.Qt.Key_Home:
                start_line = cursor.blockNumber()
                if start_line == self._get_prompt_cursor().blockNumber():
                    start_pos = self._prompt_pos
                else:
                    cursor.movePosition(QtGui.QTextCursor.StartOfBlock,
                                        QtGui.QTextCursor.KeepAnchor)
                    start_pos = cursor.position()
                    start_pos += len(self._continuation_prompt)
                    cursor.setPosition(position)
                if shift_down and self._in_buffer(position):
                    cursor.setPosition(start_pos, QtGui.QTextCursor.KeepAnchor)
                else:
                    cursor.setPosition(start_pos)
                self._set_cursor(cursor)
                intercepted = True

            elif key == QtCore.Qt.Key_Backspace:

                # Line deletion (remove continuation prompt)
                line, col = cursor.blockNumber(), cursor.columnNumber()
                if not self._reading and \
                        col == len(self._continuation_prompt) and \
                        line > self._get_prompt_cursor().blockNumber():
                    cursor.beginEditBlock()
                    cursor.movePosition(QtGui.QTextCursor.StartOfBlock,
                                        QtGui.QTextCursor.KeepAnchor)
                    cursor.removeSelectedText()
                    cursor.deletePreviousChar()
                    cursor.endEditBlock()
                    intercepted = True

                # Regular backwards deletion
                else:
                    anchor = cursor.anchor()
                    if anchor == position:
                        intercepted = not self._in_buffer(position - 1)
                    else:
                        intercepted = not self._in_buffer(min(anchor, position))

            elif key == QtCore.Qt.Key_Delete:

                # Line deletion (remove continuation prompt)
                if not self._reading and self._in_buffer(position) and \
                        cursor.atBlockEnd() and not cursor.hasSelection():
                    cursor.movePosition(QtGui.QTextCursor.NextBlock,
                                        QtGui.QTextCursor.KeepAnchor)
                    cursor.movePosition(QtGui.QTextCursor.Right,
                                        QtGui.QTextCursor.KeepAnchor,
                                        len(self._continuation_prompt))
                    cursor.removeSelectedText()
                    intercepted = True

                # Regular forwards deletion:
                else:
                    anchor = cursor.anchor()
                    intercepted = (not self._in_buffer(anchor) or
                                   not self._in_buffer(position))

        # Don't move the cursor if Control/Cmd is pressed to allow copy-paste
        # using the keyboard in any part of the buffer. Also, permit scrolling
        # with Page Up/Down keys. Finally, if we're executing, don't move the
        # cursor (if even this made sense, we can't guarantee that the prompt
        # position is still valid due to text truncation).
        if not (self._control_key_down(event.modifiers(), include_command=True)
                or key in (QtCore.Qt.Key_PageUp, QtCore.Qt.Key_PageDown)
                or (self._executing and not self._reading)):
            self._keep_cursor_in_buffer()

        return intercepted

    def execute(self, source=None, hidden=False, interactive=False):
        """ Executes source or the input buffer, possibly prompting for more
        input.
        Parameters
        ----------
        source : str, optional
            The source to execute. If not specified, the input buffer will be
            used. If specified and 'hidden' is False, the input buffer will be
            replaced with the source before execution.
        hidden : bool, optional (default False)
            If set, no output will be shown and the prompt will not be modified.
            In other words, it will be completely invisible to the user that
            an execution has occurred.
        interactive : bool, optional (default False)
            Whether the console is to treat the source as having been manually
            entered by the user. The effect of this parameter depends on the
            subclass implementation.
        Raises
        ------
        RuntimeError
            If incomplete input is given and 'hidden' is True. In this case,
            it is not possible to prompt for more input.
        Returns
        -------
        A boolean indicating whether the source was executed.
        """
        # WARNING: The order in which things happen here is very particular, in
        # large part because our syntax highlighting is fragile. If you change
        # something, test carefully!

        # Decide what to execute.
        if source is None:
            source = self.input_buffer
            if not hidden:
                # A newline is appended later, but it should be considered part
                # of the input buffer.
                source += '\n'
        elif not hidden:
            self.input_buffer = source

        # Execute the source or show a continuation prompt if it is incomplete.
        if interactive and self.execute_on_complete_input:
            complete, indent = self._is_complete(source, interactive)
        else:
            complete = True
            indent = ''
        if hidden:
            if complete or not self.execute_on_complete_input:
                self._execute(source, hidden)
                self.signaller.emit_signal(TextSignal('\n'))
                if self._prompt_html:
                    self.signaller.emit_signal(HtmlSignal(self._prompt_html))
                else:
                    self.signaller.emit_signal(TextSignal(self._prompt))
                self.signaller.emit_signal(TextSignal(source))
                self.clear()
            else:
                error = 'Incomplete noninteractive input: "%s"'
                raise RuntimeError(error % source)
        else:
            if complete:
                #self._append_plain_text('\n')
                ##################################################################################################
                cursor = self._get_end_cursor()
                cursor.insertText('\n')
                ###################################################################################################
                self._input_buffer_executing = self.input_buffer
                self._executing = True
                self._prompt_finished()

                # The maximum block count is only in effect during execution.
                # This ensures that _prompt_pos does not become invalid due to
                # text truncation.
                self._control.document().setMaximumBlockCount(self.buffer_size)

                # Setting a positive maximum block count will automatically
                # disable the undo/redo history, but just to be safe:
                self._control.setUndoRedoEnabled(False)

                # Perform actual execution.
                self._execute(source, hidden)
                self.signaller.emit_signal(TextSignal('\n'))
                if self._prompt_html:
                    self.signaller.emit_signal(HtmlSignal(self._prompt_html))
                else:
                    self.signaller.emit_signal(TextSignal(self._prompt))
                self.signaller.emit_signal(TextSignal(source))
                self.clear()

            else:
                # Do this inside an edit block so continuation prompts are
                # removed seamlessly via undo/redo.
                cursor = self._get_end_cursor()
                cursor.beginEditBlock()
                cursor.insertText('\n')
                self._insert_continuation_prompt(cursor, indent)
                cursor.endEditBlock()

                # Do not do this inside the edit block. It works as expected
                # when using a QPlainTextEdit control, but does not have an
                # effect when using a QTextEdit. I believe this is a Qt bug.
                self._control.moveCursor(QtGui.QTextCursor.End)

        return complete

# make plain controls?
PlainWidgetCreator = JupyterWidget
PlainWidgetCreator.custom_control = split_control
PlainWidgetCreator.custom_page_control = split_page_control
#PlainWidgetCreator._create_control = _create_control


def _plain_changed(self, name, old, new):
    kind = 'plain' if new else 'rich'
    self.config.ConsoleWidget.kind = kind
    if new:
        self.widget_factory = PlainWidgetCreator
    else:
        self.widget_factory = RichChatWidget


JupyterQtConsoleApp.widget_factory = RichChatWidget
JupyterQtConsoleApp._plain_changed = _plain_changed
# Test Rich
#from IPython.display import Image
#Image(filename='squirrel.png')

#qtconsoleapp.JupyterQtConsoleApp.existing = 'tester'
JupyterQtConsoleApp.launch_instance()
