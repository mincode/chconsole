from qtconsole.qt import QtCore, QtGui

from chconsole.media import get_block_plain_text
from chconsole.messages import Execute, Complete, Restart, Interrupt
from chconsole.standards import BaseEventFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def complete_possible(cursor):
    """
    Determine whether there is text before the cursor position that may be completed.
    :param cursor: position.
    :return: True if there is non-whitespace text immediately before the cursor.
    """
    text = get_block_plain_text(cursor.block())
    return bool(text[:cursor.columnNumber()].strip())


class CodeAreaFilter(BaseEventFilter):
    def __init__(self, target):
        super(CodeAreaFilter, self).__init__(target)

    def eventFilter(self, obj, event):
        intercepted = False

        if event.type() == QtCore.QEvent.KeyPress:
            intercepted = True  # eat the key by default
            key = event.key()
            alt_down = event.modifiers() & QtCore.Qt.AltModifier
            shift_down = event.modifiers() & QtCore.Qt.ShiftModifier
            ctrl_down = self.control_key_down(event.modifiers())

            if event.matches(QtGui.QKeySequence.Copy):
                self.target.copy()
            elif event.matches(QtGui.QKeySequence.Cut):
                self.target.cut()
            elif event.matches(QtGui.QKeySequence.Paste):
                self.target.paste()

            #------ Special modifier logic -----------------------------------------

            elif key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                # Special handling when tab completing in text mode.
                self.target.completer.cancel_completion()

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
                    self.target.please_export.emit(Execute(self.target.source))
                    self.target.history.store(self.target.source)
                    self.target.clear()
                elif self.target.execute_on_complete_input and (at_end or single_line):
                    # Python seems to expect \n at the end of multi-line code to properly decide
                    # that it is complete. For single-line code the terminating \n is irrelevant.
                    # The \n does not seem to be needed for executint code.
                    complete, indent = self.target.is_complete(self.target.source.code + '\n')
                    if complete:
                        self.target.please_export.emit(Execute(self.target.source))
                        self.target.history.store(self.target.source)
                        self.target.clear()
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

                elif key == QtCore.Qt.Key_Y:
                    self.target.kill_ring.rotate()

                elif key == QtCore.Qt.Key_Backspace:
                    cursor = self.target.word_start_cursor
                    position = self.target.textCursor().position()
                    cursor.setPosition(position, QtGui.QTextCursor.KeepAnchor)
                    self.target.kill_ring.kill_cursor(cursor)

                elif key in (QtCore.Qt.Key_D, QtCore.Qt.Key_Delete):
                    cursor = self.target.word_end_cursor
                    position = self.target.textCursor().position()
                    cursor.setPosition(position, QtGui.QTextCursor.KeepAnchor)
                    self.target.target.kill_ring.kill_cursor(cursor)

            elif ctrl_down:
                if key == QtCore.Qt.Key_I:
                    self.target.please_export.emit(Interrupt())

                elif key == QtCore.Qt.Key_G:
                    self.target.please_export.emit(Restart(self.target.clear_on_kernel_restart))

                elif key == QtCore.Qt.Key_O:
                    self.target.release_focus.emit()

                elif key == QtCore.Qt.Key_D:
                    new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Delete, QtCore.Qt.NoModifier)
                    QtGui.qApp.sendEvent(self._control, new_event)

                # Kill ring
                elif key == QtCore.Qt.Key_K:
                    cursor = self.target.textCursor()
                    cursor.clearSelection()
                    cursor.movePosition(QtGui.QTextCursor.EndOfLine,
                                        QtGui.QTextCursor.KeepAnchor)
                    if not cursor.hasSelection():
                        # Line deletion
                        cursor.movePosition(QtGui.QTextCursor.NextBlock,
                                            QtGui.QTextCursor.KeepAnchor)
                    self.target.kill_ring.kill_cursor(cursor)
                    self.target.setTextCursor(cursor)

                elif key == QtCore.Qt.Key_U:
                    cursor = self.target.textCursor()
                    cursor.clearSelection()
                    cursor.movePosition(QtGui.QTextCursor.StartOfBlock,
                                        QtGui.QTextCursor.KeepAnchor)
                    self.target.kill_ring.kill_cursor(cursor)
                    self.target.setTextCursor(cursor)

                elif key == QtCore.Qt.Key_Y:
                    self.target.kill_ring.yank()

                elif key == QtCore.Qt.Key_Backspace:
                    cursor = self.target.word_start_cursor
                    position = self.target.textCursor().position()
                    cursor.setPosition(position, QtGui.QTextCursor.KeepAnchor)
                    self.target.kill_ring.kill_cursor(cursor)

                elif key == QtCore.Qt.Key_Delete:
                    cursor = self.target.word_end_cursor
                    position = self.target.textCursor().position()
                    cursor.setPosition(position, QtGui.QTextCursor.KeepAnchor)
                    self.target.target.kill_ring.kill_cursor(cursor)

            else:
                anchor_mode = QtGui.QTextCursor.KeepAnchor if shift_down else QtGui.QTextCursor.MoveAnchor

                if key == QtCore.Qt.Key_Tab:
                    if self.target.textCursor().position() == 0:
                        self.target.to_next.emit()
                    elif complete_possible(self.target.textCursor()):
                        self.target.please_export.emit(Complete(self.target.source,
                                                                self.target.textCursor().position()))
                    else:
                        self.target.insertPlainText(' '*self.target.tab_width)

                elif key == QtCore.Qt.Key_Down:
                    self.target.moveCursor(QtGui.QTextCursor.Down, anchor_mode)

                elif key == QtCore.Qt.Key_Up:
                    self.target.moveCursor(QtGui.QTextCursor.Up, anchor_mode)

                elif key == QtCore.Qt.Key_Right:
                    self.target.moveCursor(QtGui.QTextCursor.Right, anchor_mode)

                elif key == QtCore.Qt.Key_Left:
                    self.target.moveCursor(QtGui.QTextCursor.Left, anchor_mode)

                elif key == QtCore.Qt.Key_Escape:
                    self.target.clear()

                # Smart backspace: remove target.tabwidth (usually four) characters in one backspace if:
                # 1) everything left of the cursor is whitespace
                # 2) the target.tabwidth characters immediately left of the cursor are spaces
                # There is a slight inconsistency because for indentation the suggested indent blanks replied
                # by the kernel are used which are not coordinated with target.tabwidth. It would be better if
                # the indents by the kernel are multiples of target.tabwidth.
                elif key == QtCore.Qt.Key_Backspace:
                    remove_smart = self.target.tab_width
                    cursor = self.target.textCursor()
                    col = cursor.columnNumber()
                    if cursor.hasSelection():
                            cursor.removeSelectedText()
                    else:
                        if col < remove_smart:
                            cursor.movePosition(QtGui.QTextCursor.Left,
                                                QtGui.QTextCursor.KeepAnchor)
                            cursor.removeSelectedText()
                        else:
                            cursor.movePosition(cursor.StartOfLine, cursor.KeepAnchor)
                            text = cursor.selectedText()
                            if text.endswith(' '*remove_smart) and not text.strip():
                                chars = remove_smart
                            else:
                                chars = 1
                            cursor = self.target.textCursor()
                            cursor.movePosition(QtGui.QTextCursor.Left,
                                                QtGui.QTextCursor.KeepAnchor, chars)
                            cursor.removeSelectedText()

                else:
                    # accept other keys as text entered by the user
                    intercepted = False

        return intercepted
