from qtconsole.qt import QtCore, QtGui
from .base_event_filter import BaseEventFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


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
        else:
            error = 'Incomplete noninteractive input: "%s"'
            raise RuntimeError(error % source)
    else:
        if complete:
            self._append_plain_text('\n')
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

        if self._control_key_down(event.modifiers(), include_command=False):

            if key == QtCore.Qt.Key_C and self._executing:
                self.request_interrupt_kernel()
                return True

            elif key == QtCore.Qt.Key_Period:
                self.request_restart_kernel()
                return True

        elif not event.modifiers() & QtCore.Qt.AltModifier:

            # Smart backspace: remove four characters in one backspace if:
            # 1) everything left of the cursor is whitespace
            # 2) the four characters immediately left of the cursor are spaces
            if key == QtCore.Qt.Key_Backspace:
                col = self._get_input_buffer_cursor_column()
                cursor = self._control.textCursor()
                if col > 3 and not cursor.hasSelection():
                    text = self._get_input_buffer_cursor_line()[:col]
                    if text.endswith('    ') and not text.strip():
                        cursor.movePosition(QtGui.QTextCursor.Left,
                                            QtGui.QTextCursor.KeepAnchor, 4)
                        cursor.removeSelectedText()
                        return True

   def _tab_pressed(self):
        """ Called when the tab key is pressed. Returns whether to continue
            processing the event.
        """
        # Perform tab completion if:
        # 1) The cursor is in the input buffer.
        # 2) There is a non-whitespace character before the cursor.
        text = self._get_input_buffer_cursor_line()
        if text is None:
            return False
        complete = bool(text[:self._get_input_buffer_cursor_column()].strip())
        if complete:
            self._complete()
        return not complete


class EntryFilter(BaseEventFilter):
    def __init__(self, target):
        super(EntryFilter, self).__init__(target)

    def eventFilter(self, obj, event):
        intercepted = False
        event_type = event.type()

        if event_type == QtCore.QEvent.KeyPress:
            intercepted = True  # eat the key by default
            key = event.key()
            alt_down = event.modifiers() & QtCore.Qt.AltModifier
            shift_down = event.modifiers() & QtCore.Qt.ShiftModifier
            ctrl_down = self.control_key_down(event.modifiers())

            if event.matches(QtGui.QKeySequence.Copy):
                self.target.copy()
            elif event.matches(QtGui.QKeySequence.Cut):
                self.cut()
            elif event.matches(QtGui.QKeySequence.Paste):
                self.paste()

            #------ Special modifier logic -----------------------------------------

            elif key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                # Special handling when tab completing in text mode.
                self.target.completer.cancel_completion()

    #MM: later
                # Special handling when a reading a line of raw input.
                # if self._reading:
                #     self._append_plain_text('\n')
                #     self._reading = False
                #     if self._reading_callback:
                #         self._reading_callback()

                # If the input buffer is a single line or there is only
                # whitespace after the cursor, execute. Otherwise, split the
                # line with a continuation prompt.
                cursor = self.target.textCursor()
                cursor.movePosition(QtGui.QTextCursor.End,
                                    QtGui.QTextCursor.KeepAnchor)
                at_end = len(cursor.selectedText().strip()) == 0

                single_line = self.target.document().blockCount() == 1

                if ctrl_down:
                    # no indent, no execute
                    self.target.insertPlainText('\n')
                    self.target.moveCursor(QtGui.QTextCursor.End)
                    self.target.ensureCursorVisible()
                elif shift_down:
                    # force execute source
                    source = self.target.document().toPlainText()
                    self.target.execute(source)
                elif self.target.execute_on_complete_input and (at_end or single_line):
                    source = self.target.document().toPlainText()
                    complete, indent = self.target.is_complete(source)
                    if complete:
                        self.execute(source)
                    else:
                        self.target.insertPlainText('\n')
                        self.target.insertPlainText(indent)
                        self.target.moveCursor(QtGui.QTextCursor.End)
                        self.target.ensureCursorVisible()

            elif alt_down:
                if key == QtCore.Qt.Key_Greater:
                    self.target.moveCursor(QtGui.QTextCursor.End)

                elif key == QtCore.Qt.Key_Less:
                    self.target.moveCursor(QtGui.QTextCursor.Start)

                elif key == QtCore.Qt.Key_B:
                    self.target.setTextCursor(self.target.word_start_cursor)

                elif key == QtCore.Qt.Key_F:
                    self.target.setTextCursor(self.target.word_end_cursor)

            elif ctrl_down:
                if key == QtCore.Qt.Key_O:
                    self.target.release_focus.emit()

            else:
                anchor_mode = QtGui.QTextCursor.KeepAnchor if shift_down else QtGui.QTextCursor.MoveAnchor

                if key == QtCore.Qt.Key_Down:
                    self.target.moveCursor(QtGui.QTextCursor.Down, anchor_mode)
                elif key == QtCore.Qt.Key_Up:
                    self.target.moveCursor(QtGui.QTextCursor.Up, anchor_mode)
                elif key == QtCore.Qt.Key_Right:
                    self.target.moveCursor(QtGui.QTextCursor.Right, anchor_mode)
                elif key == QtCore.Qt.Key_Left:
                    self.target.moveCursor(QtGui.QTextCursor.Left, anchor_mode)

                # vi/less -like key bindings
                elif key == QtCore.Qt.Key_J:
                    new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                                QtCore.Qt.Key_Down,
                                                QtCore.Qt.NoModifier)
                    QtGui.qApp.sendEvent(self.target, new_event)

                # vi/less -like key bindings
                elif key == QtCore.Qt.Key_K:
                    new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                                QtCore.Qt.Key_Up,
                                                QtCore.Qt.NoModifier)
                    QtGui.qApp.sendEvent(self.target, new_event)
                else:
                    # accept other keys as text entered by the user
                    intercepted = False

        return intercepted
