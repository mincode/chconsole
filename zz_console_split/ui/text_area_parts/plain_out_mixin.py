from qtconsole.qt import QtCore, QtGui
from .base_event_filter import BaseEventFilter, control_key_down
from .context_menu import ContextMenu
__author__ = 'Manfred Minimair <manfred@minimair.org>'


class _TextAreaFilter(BaseEventFilter):
    def __init__(self, text_area):
        super().__init__(text_area)

    def eventFilter(self, obj, event):
        """ Filter key events for the underlying text widget to create a
            console-like interface.
        """
        intercepted = False
#         cursor = self._control.textCursor()
#         position = cursor.position()
#         key = event.key()
#         ctrl_down = control_key_down(event.modifiers())
#         alt_down = event.modifiers() & QtCore.Qt.AltModifier
#         shift_down = event.modifiers() & QtCore.Qt.ShiftModifier
#
#         #------ Special sequences ----------------------------------------------
#
#         if event.matches(QtGui.QKeySequence.Copy):
#             self.copy()
#             intercepted = True
#
#         #------ Special modifier logic -----------------------------------------
# #Later: plain_in
#         # elif key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
#         #     intercepted = True
#         #
#         #     # Special handling when tab completing in text mode.
#         #     self._cancel_completion()
#         #
#         #     if self._in_buffer(position):
#         #         # Special handling when a reading a line of raw input.
#         #         if self._reading:
#         #             self._append_plain_text('\n')
#         #             self._reading = False
#         #             if self._reading_callback:
#         #                 self._reading_callback()
#         #
#         #         # If the input buffer is a single line or there is only
#         #         # whitespace after the cursor, execute. Otherwise, split the
#         #         # line with a continuation prompt.
#         #         elif not self._executing:
#         #             cursor.movePosition(QtGui.QTextCursor.End,
#         #                                 QtGui.QTextCursor.KeepAnchor)
#         #             at_end = len(cursor.selectedText().strip()) == 0
#         #             single_line = (self._get_end_cursor().blockNumber() ==
#         #                            self._get_prompt_cursor().blockNumber())
#         #             if (at_end or shift_down or single_line) and not ctrl_down:
#         #                 self.execute(interactive = not shift_down)
#         #             else:
#         #                 # Do this inside an edit block for clean undo/redo.
#         #                 cursor.beginEditBlock()
#         #                 cursor.setPosition(position)
#         #                 cursor.insertText('\n')
#         #                 self._insert_continuation_prompt(cursor)
#         #                 cursor.endEditBlock()
#         #
#         #                 # Ensure that the whole input buffer is visible.
#         #                 # FIXME: This will not be usable if the input buffer is
#         #                 # taller than the console widget.
#         #                 self._control.moveCursor(QtGui.QTextCursor.End)
#         #                 self._control.setTextCursor(cursor)
#
#
#         #------ Alt modifier ---------------------------------------------------
#
#         elif alt_down:
#             if key == QtCore.Qt.Key_B:
#                 self._set_cursor(self._get_word_start_cursor(position))
#                 intercepted = True
#
#             elif key == QtCore.Qt.Key_F:
#                 self._set_cursor(self._get_word_end_cursor(position))
#                 intercepted = True
#
#             elif key == QtCore.Qt.Key_Delete:
#                 intercepted = True
#
#             elif key == QtCore.Qt.Key_Greater:
#                 self._control.moveCursor(QtGui.QTextCursor.End)
#                 intercepted = True
#
#             elif key == QtCore.Qt.Key_Less:
#                 self._control.moveCursor(QtGui.QTextCursor.Start)
#                 intercepted = True
#
#         #------ No modifiers ---------------------------------------------------
#
#         else:
#             if shift_down:
#                 anchormode = QtGui.QTextCursor.KeepAnchor
#             else:
#                 anchormode = QtGui.QTextCursor.MoveAnchor
#
#             if key == QtCore.Qt.Key_Left:
#
#                 # Move to the previous line
#                 line, col = cursor.blockNumber(), cursor.columnNumber()
#                 if line > self._get_prompt_cursor().blockNumber() and \
#                         col == len(self._continuation_prompt):
#                     self._control.moveCursor(QtGui.QTextCursor.PreviousBlock,
#                                              mode=anchormode)
#                     self._control.moveCursor(QtGui.QTextCursor.EndOfBlock,
#                                              mode=anchormode)
#                     intercepted = True
#
#                 # Regular left movement
#                 else:
#                     intercepted = not self._in_buffer(position - 1)
#
#             elif key == QtCore.Qt.Key_Right:
#                 original_block_number = cursor.blockNumber()
#                 self._control.moveCursor(QtGui.QTextCursor.Right,
#                                 mode=anchormode)
#                 if cursor.blockNumber() != original_block_number:
#                     self._control.moveCursor(QtGui.QTextCursor.Right,
#                                         n=len(self._continuation_prompt),
#                                         mode=anchormode)
#                 intercepted = True
#
#             elif key == QtCore.Qt.Key_Home:
#                 start_line = cursor.blockNumber()
#                 if start_line == self._get_prompt_cursor().blockNumber():
#                     start_pos = self._prompt_pos
#                 else:
#                     cursor.movePosition(QtGui.QTextCursor.StartOfBlock,
#                                         QtGui.QTextCursor.KeepAnchor)
#                     start_pos = cursor.position()
#                     start_pos += len(self._continuation_prompt)
#                     cursor.setPosition(position)
#                 if shift_down and self._in_buffer(position):
#                     cursor.setPosition(start_pos, QtGui.QTextCursor.KeepAnchor)
#                 else:
#                     cursor.setPosition(start_pos)
#                 self._set_cursor(cursor)
#                 intercepted = True
#
#             elif key == QtCore.Qt.Key_Backspace:
#
#                 # Line deletion (remove continuation prompt)
#                 line, col = cursor.blockNumber(), cursor.columnNumber()
#                 if not self._reading and \
#                         col == len(self._continuation_prompt) and \
#                         line > self._get_prompt_cursor().blockNumber():
#                     cursor.beginEditBlock()
#                     cursor.movePosition(QtGui.QTextCursor.StartOfBlock,
#                                         QtGui.QTextCursor.KeepAnchor)
#                     cursor.removeSelectedText()
#                     cursor.deletePreviousChar()
#                     cursor.endEditBlock()
#                     intercepted = True
#
#                 # Regular backwards deletion
#                 else:
#                     anchor = cursor.anchor()
#                     if anchor == position:
#                         intercepted = not self._in_buffer(position - 1)
#                     else:
#                         intercepted = not self._in_buffer(min(anchor, position))
#
        return intercepted


class PlainOutMixin(object):
    text_area_filter = None
    viewport_filter = None

    def __init__(self):
        self.text_area_filter = _TextAreaFilter(self)
        self.installEventFilter(self.text_area_filter)

    def context_menu(self, pos, input_target, allow_paste=True):
        return ContextMenu(self, pos, input_target, allow_paste=True)
