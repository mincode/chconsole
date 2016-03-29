from qtconsole.qt import QtCore, QtGui

from chconsole.media import get_block_plain_text
from chconsole.messages import Execute
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


class ChatAreaFilter(BaseEventFilter):
    def __init__(self, target):
        super(ChatAreaFilter, self).__init__(target)

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
                else:
                    # force execute source
                    self.target.please_export.emit(Execute(self.target.source))
                    self.target.clear()

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

                elif key == QtCore.Qt.Key_D:
                    new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Delete, QtCore.Qt.NoModifier)
                    QtGui.qApp.sendEvent(self.target, new_event)

            else:
                anchor_mode = QtGui.QTextCursor.KeepAnchor if shift_down else QtGui.QTextCursor.MoveAnchor

                if key == QtCore.Qt.Key_Tab:
                    if self.target.textCursor().position() == 0:
                        self.target.to_next.emit()
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

                else:
                    # accept other keys as text entered by the user
                    intercepted = False

        return intercepted
