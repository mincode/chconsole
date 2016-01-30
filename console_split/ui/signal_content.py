from functools import singledispatch
from traitlets import Bool
from qtconsole.qt import QtGui
from qtconsole.console_widget import ConsoleWidget
from qtconsole.ansi_code_processor import QtAnsiCodeProcessor

__author__ = 'minimair'

PROCESS_ANSI_CODES = Bool(True, config=True, help="Whether to process ANSI escape codes.")


def _set_top_cursor(target, cursor):
    """ Scrolls the viewport so that the specified cursor is at the top of target.
    """
    scrollbar = target.verticalScrollBar()
    scrollbar.setValue(scrollbar.maximum())
    original_cursor = target.textCursor()
    target.setTextCursor(cursor)
    target.ensureCursorVisible()
    target.setTextCursor(original_cursor)


class SignalContent:
    """
    Wrapper for data needed to output with Qt signals.
    """
    # Per class member
    ansi_processor = QtAnsiCodeProcessor()
    # object data
    message = None
    ansi_codes = None

    def __init__(self, message, ansi_codes=PROCESS_ANSI_CODES):
        self.message = message
        self.ansi_codes = ansi_codes


class TextSignal(SignalContent):
    pass


class HtmlSignal(SignalContent):
    pass


@singledispatch
def insert_signal_content(output, target):
    raise NotImplementedError


@insert_signal_content.register(TextSignal)
def _(output, target):
    if output.message:
        cursor = target.textCursor()
        text = output.message
        # adopted from qtconsole.console_widget._insert_plain_text(self, cursor, text, flush=False)
        cursor.beginEditBlock()
        if output.ansi_codes:
            for substring in output.ansi_processor.split_string(text):
                for act in output.ansi_processor.actions:
                    #print(act)

                    # Unlike real terminal emulators, we don't distinguish
                    # between the screen and the scrollback buffer. A screen
                    # erase request clears everything.
                    if act.action == 'erase' and act.area == 'screen':
                        cursor.select(QtGui.QTextCursor.Document)
                        cursor.removeSelectedText()

                    # Simulate a form feed by scrolling just past the last line.
                    elif act.action == 'scroll' and act.unit == 'page':
                        cursor.insertText('\n')
                        cursor.endEditBlock()
                        _set_top_cursor(target, cursor)
                        cursor.joinPreviousEditBlock()
                        cursor.deletePreviousChar()

                    elif act.action == 'carriage-return':
                        cursor.movePosition(
                            cursor.StartOfLine, cursor.KeepAnchor)

                    elif act.action == 'beep':
                        QtGui.qApp.beep()

                    elif act.action == 'backspace':
                        if not cursor.atBlockStart():
                            cursor.movePosition(
                                cursor.PreviousCharacter, cursor.KeepAnchor)

                    elif act.action == 'newline':
                        cursor.movePosition(cursor.EndOfLine)

                out_format = output.ansi_processor.get_format()

                selection = cursor.selectedText()
                if len(selection) == 0:
                    cursor.insertText(substring, out_format)
                elif substring is not None:
                    # BS and CR are treated as a change in print
                    # position, rather than a backwards character
                    # deletion for output equivalence with (I)Python
                    # terminal.
                    if len(substring) >= len(selection):
                        cursor.insertText(substring, out_format)
                    else:
                        old_text = selection[len(substring):]
                        cursor.insertText(substring + old_text, out_format)
                        cursor.movePosition(cursor.PreviousCharacter, cursor.KeepAnchor, len(old_text))
        else:
            cursor.insertText(text)
        cursor.endEditBlock()
        #target.insertPlainText(output.content)


@insert_signal_content.register(HtmlSignal)
def _(output, target):
    if output.message:
        #target.insertHtml(output.content)
        #print(type(target))
        ConsoleWidget._insert_html(None, target.textCursor(), output.message)