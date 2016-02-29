import sys
from unicodedata import category
from traitlets.config.configurable import LoggingConfigurable
from traitlets import Integer, Unicode, Instance, DottedObjectName, Any, Float
from ipython_genutils import py3compat
from ipython_genutils.importstring import import_item
from qtconsole.qt import QtGui, QtCore
from qtconsole.ansi_code_processor import QtAnsiCodeProcessor
from qtconsole.util import get_font
from qtconsole import styles
from qtconsole.pygments_highlighter import PygmentsHighlighter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


# ConsoleWdidget
def is_letter_or_number(char):
    """ Returns whether the specified unicode character is a letter or a number.
    """
    cat = category(char)
    return cat.startswith('L') or cat.startswith('N')


# adopted from ConsoleWidget
def _set_top_cursor(receiver, cursor):
    """ Scrolls the viewport so that the specified cursor is at the top.
    """
    scrollbar = receiver.verticalScrollBar()
    scrollbar.setValue(scrollbar.maximum())
    original_cursor = receiver.textCursor()
    receiver.setTextCursor(cursor)
    receiver.ensureCursorVisible()
    receiver.setTextCursor(original_cursor)


# ConsoleWidget
def get_block_plain_text(block):
    """ Given a QTextBlock, return its unformatted text.
    """
    cursor = QtGui.QTextCursor(block)
    cursor.movePosition(QtGui.QTextCursor.StartOfBlock)
    cursor.movePosition(QtGui.QTextCursor.EndOfBlock,
                        QtGui.QTextCursor.KeepAnchor)
    return cursor.selection().toPlainText()

# FrontendWidget
class FrontendHighlighter(PygmentsHighlighter):
    """ A PygmentsHighlighter that understands and ignores prompts.
    """
    _current_offset = 0
    _frontend = None  # QTextEdit or QPlainTextEdit
    highlight_on = False  # whether to highlight

    def __init__(self, frontend, lexer=None):
        super(FrontendHighlighter, self).__init__(frontend.document(), lexer=lexer)
        self._current_offset = 0
        self._frontend = frontend
        self.highlighting_on = False

    def highlightBlock(self, string):
        """ Highlight a block of text. Reimplemented to highlight selectively.
        """
        if not self.highlighting_on:
            return

        # The input to this function is a unicode string that may contain
        # paragraph break characters, non-breaking spaces, etc. Here we acquire
        # the string as plain text so we can compare it.
        current_block = self.currentBlock()
        string = get_block_plain_text(current_block)

# Potentially handle prompt differently
        # # Decide whether to check for the regular or continuation prompt.
        # if current_block.contains(self._frontend._prompt_pos):
        #     prompt = self._frontend._prompt
        # else:
        #     prompt = self._frontend._continuation_prompt
        #
        # # Only highlight if we can identify a prompt, but make sure not to
        # # highlight the prompt.
        # if string.startswith(prompt):
        #    self._current_offset = len(prompt)
        #    string = string[len(prompt):]
        super(FrontendHighlighter, self).highlightBlock(string)

    def rehighlightBlock(self, block):
        """ Reimplemented to temporarily enable highlighting if disabled.
        """
        old = self.highlighting_on
        self.highlighting_on = True
        super(FrontendHighlighter, self).rehighlightBlock(block)
        self.highlighting_on = old

    def setFormat(self, start, count, format):
        """ Reimplemented to highlight selectively.
        """
        start += self._current_offset
        super(FrontendHighlighter, self).setFormat(start, count, format)


class TextConfig(LoggingConfigurable):
    """
    Mixin for configuring text properties of a QTextEdit or QPlainTextEdit.
    """
    font_family = Unicode(
        config=True,
        help="""The font family to use for the console.
        On OSX this defaults to Monaco, on Windows the default is
        Consolas with fallback of Courier, and on other platforms
        the default is Monospace.
        """)

    font_size = Integer(
        config=True, help="The font size. If unconfigured, Qt will be entrusted with the size of the font.")

    standard_tab_width = Integer(8, config=True, help="Number of spaces used for tab.")

    style_sheet = Unicode(config=True,
        help="""
        A CSS stylesheet. The stylesheet can contain classes for:
            1. Qt: QPlainTextEdit, QFrame, QWidget, etc
            2. Pygments: .c, .k, .o, etc. (see PygmentsHighlighter)
            3. QtConsole: .error, .in-prompt, .out-prompt, etc
        """)

    syntax_style = Unicode(config=True,
        help="""
        If not empty, use this Pygments style for syntax highlighting.
        Otherwise, the style sheet is queried for Pygments style
        information.
        """)

    _highlighter = Instance(FrontendHighlighter, allow_none=True)

    lexer_class = DottedObjectName(config=True,
        help="The pygments lexer class to use."
    )

    is_complete_timeout = Float(0.25, config=True,
        help="Seconds to wait for is_complete replies from the kernel."
    )

    lexer = Any()

    ansi_processor = None  # QtAnsiCodeProcessor

    increase_font_size = None  # action for increasing font size
    decrease_font_size = None  # action for decreasing font size
    reset_font_size = None  # action for resetting font size

    def __init__(self, **kwargs):
        """
        Initialize.
        :return:
        """
        super(LoggingConfigurable, self).__init__(**kwargs)

        self.setMouseTracking(True)
        if hasattr(self, 'setAcceptRichText'):
            self.setAcceptRichText(False)

        self.setAttribute(QtCore.Qt.WA_InputMethodEnabled, True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setReadOnly(False)
        self.setUndoRedoEnabled(False)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        # ConsoleWidget
        # Hijack the document size change signal to prevent Qt from adjusting
        # the viewport's scrollbar. We are relying on an implementation detail
        # of Q(Plain)TextEdit here, which is potentially dangerous, but without
        # this functionality we cannot create a nice terminal interface.
        layout = self.document().documentLayout()
        layout.documentSizeChanged.disconnect()
        layout.documentSizeChanged.connect(self.adjust_scrollbars)

        self.ansi_processor = QtAnsiCodeProcessor()

        # JupyterWidget
        # Initialize widget styling.
        if self.style_sheet:
            self._style_sheet_changed()
            self._syntax_style_changed()
        else:
            self.set_default_style()

        self._highlighter = FrontendHighlighter(self, lexer=self.lexer)

        self.increase_font_size = QtGui.QAction("Bigger Font",
                self,
                shortcut=QtGui.QKeySequence.ZoomIn,
                shortcutContext=QtCore.Qt.WidgetWithChildrenShortcut,
                statusTip="Increase the font size by one point",
                triggered=self._increase_font_size)
        self.addAction(self.increase_font_size)

        self.increase_font_size = QtGui.QAction("Bigger Font",
                self,
                shortcut="Ctrl+=",
                shortcutContext=QtCore.Qt.WidgetWithChildrenShortcut,
                statusTip="Increase the font size by one point",
                triggered=self._increase_font_size)
        self.addAction(self.increase_font_size)

        self.decrease_font_size = QtGui.QAction("Smaller Font",
                self,
                shortcut=QtGui.QKeySequence.ZoomOut,
                shortcutContext=QtCore.Qt.WidgetWithChildrenShortcut,
                statusTip="Decrease the font size by one point",
                triggered=self._decrease_font_size)
        self.addAction(self.decrease_font_size)

        self.reset_font_size = QtGui.QAction("Normal Font",
                self,
                shortcut="Ctrl+0",
                shortcutContext=QtCore.Qt.WidgetWithChildrenShortcut,
                statusTip="Restore the Normal font size",
                triggered=self.reset_font)
        self.addAction(self.reset_font_size)

        # Set a monospaced font.
        self.reset_font()

    # ConsoleWidget
    def adjust_scrollbars(self):
        """ Expands the vertical scrollbar beyond the range set by Qt.
        """
        # This code is adapted from _q_adjustScrollbars in qplaintextedit.cpp
        # and qtextedit.cpp.
        document = self.document()
        scrollbar = self.verticalScrollBar()
        viewport_height = self.viewport().height()
        if isinstance(self, QtGui.QPlainTextEdit):
            maximum = max(0, document.lineCount() - 1)
            step = viewport_height / self.fontMetrics().lineSpacing()
        else:
            # QTextEdit does not do line-based layout and blocks will not in
            # general have the same height. Therefore it does not make sense to
            # attempt to scroll in line height increments.
            maximum = document.size().height()
            step = viewport_height
        diff = maximum - scrollbar.maximum()
        scrollbar.setRange(0, maximum)
        scrollbar.setPageStep(step)

        # Compensate for undesirable scrolling that occurs automatically due to
        # maximumBlockCount() text truncation.
        if diff < 0 and document.blockCount() == document.maximumBlockCount():
            scrollbar.setValue(scrollbar.value() + diff)

    @staticmethod
    def _font_family_default():
        if sys.platform == 'win32':
            # Consolas ships with Vista/Win7, fallback to Courier if needed
            return 'Consolas'
        elif sys.platform == 'darwin':
            # OSX always has Monaco, no need for a fallback
            return 'Monaco'
        else:
            # Monospace should always exist, no need for a fallback
            return 'Monospace'

    def reset_font(self):
        """
        Sets the font to the default fixed-width font for this platform.
        """
        fallback = self._font_family_default()
        font = get_font(self.font_family, fallback)
        if self.font_size:
            font.setPointSize(self.font_size)
        else:
            font.setPointSize(QtGui.qApp.font().pointSize())
        font.setStyleHint(QtGui.QFont.TypeWriter)
        self._set_font(font)

    def _get_font(self):
        """ The base font being used.
        """
        return self.document().defaultFont()

    def _set_font(self, font):
        """ Sets the base font for the ConsoleWidget to the specified QFont.
        """
        font_metrics = QtGui.QFontMetrics(font)
        self.setTabStopWidth(self.tab_width * font_metrics.width(' '))

        # self._completion_widget.setFont(font)
        self.document().setDefaultFont(font)
        # if self._page_control:
        #     self._page_control.document().setDefaultFont(font)

        # self.font_changed.emit(font)

    font = property(_get_font, _set_font)

    def change_font_size(self, delta):
        """Change the font size by the specified amount (in points).
        """
        font = self.font
        size = max(font.pointSize() + delta, 1)  # minimum 1 point
        font.setPointSize(size)
        self._set_font(font)

    def _increase_font_size(self):
        self.change_font_size(1)

    def _decrease_font_size(self):
        self.change_font_size(-1)

    def _get_tab_width(self):
        """ The width (in terms of space characters) for tab characters.
        """
        return self.standard_tab_width

    def _set_tab_width(self, tab_width):
        """ Sets the width (in terms of space characters) for tab characters.
        """
        font_metrics = QtGui.QFontMetrics(self.font)
        self.setTabStopWidth(tab_width * font_metrics.width(' '))

        self.standard_tab_width = tab_width

    tab_width = property(_get_tab_width, _set_tab_width)

    #JupyterWidget
    def set_default_style(self, colors='lightbg'):
        """ Sets the widget style to the class defaults.

        Parameters
        ----------
        colors : str, optional (default lightbg)
            Whether to use the default light background or dark
            background or B&W style.
        """
        colors = colors.lower()
        if colors=='lightbg':
            self.style_sheet = styles.default_light_style_sheet
            self.syntax_style = styles.default_light_syntax_style
        elif colors=='linux':
            self.style_sheet = styles.default_dark_style_sheet
            self.syntax_style = styles.default_dark_syntax_style
        elif colors=='nocolor':
            self.style_sheet = styles.default_bw_style_sheet
            self.syntax_style = styles.default_bw_syntax_style
        else:
            raise KeyError("No such color scheme: %s"%colors)

    # traitlets

    # JupyterWidget
    def _style_sheet_changed(self):
        """ Set the style sheets of the underlying widgets.
        """
        self.setStyleSheet(self.style_sheet)
        self.document().setDefaultStyleSheet(self.style_sheet)
        bg_color = self.palette().window().color()
        self.ansi_processor.set_background_color(bg_color)

        # if self._page_control is not None:
        #     self._page_control.document().setDefaultStyleSheet(self.style_sheet)

    # JupyterWidget
    def _syntax_style_changed(self):
        """ Set the style for the syntax highlighter.
        """
        if self._highlighter is None:
            # ignore premature calls
            return
        if self.syntax_style:
            self._highlighter.set_style(self.syntax_style)
        else:
            self._highlighter.set_style_sheet(self.style_sheet)

    # FrontendWidget
    def _lexer_class_changed(self, name, old, new):
        lexer_class = import_item(new)
        self.lexer = lexer_class()

    # FrontendWidget
    def _lexer_class_default(self):
        if py3compat.PY3:
            return 'pygments.lexers.Python3Lexer'
        else:
            return 'pygments.lexers.PythonLexer'

    # FrontendWidget
    def _lexer_default(self):
        lexer_class = import_item(self.lexer_class)
        return lexer_class()

    # adopted from ConsoleWidget
    def insert_ansi_text(self, text, ansi_codes=True, cursor=None):
        cursor = cursor if cursor else self.textCursor()
        cursor.beginEditBlock()
        if ansi_codes:
            for substring in self.ansi_processor.split_string(text):
                for act in self.ansi_processor.actions:

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
                        _set_top_cursor(self, cursor)
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

                ansi_format = self.ansi_processor.get_format()

                selection = cursor.selectedText()
                if len(selection) == 0:
                    cursor.insertText(substring, ansi_format)
                elif substring is not None:
                    # BS and CR are treated as a change in print
                    # position, rather than a backwards character
                    # deletion for output equivalence with (I)Python
                    # terminal.
                    if len(substring) >= len(selection):
                        cursor.insertText(substring, ansi_format)
                    else:
                        old_text = selection[len(substring):]
                        cursor.insertText(substring + old_text, ansi_format)
                        cursor.movePosition(cursor.PreviousCharacter, cursor.KeepAnchor, len(old_text))
        else:
            cursor.insertText(text)
        cursor.endEditBlock()

    # ConsoleWidget
    def insert_html(self, html, cursor=None):
        """
        Inserts HTML using the specified cursor in such a way that future
            formatting is unaffected.
        :param html:
        :param cursor:
        :return:
        """
        cursor = cursor if cursor else self.textCursor()
        cursor.beginEditBlock()
        cursor.insertHtml(html)

        # Remark from qtconsole.console_widget:
        # After inserting HTML, the text document "remembers" it's in "html
        # mode", which means that subsequent calls adding plain text will result
        # in unwanted formatting, lost tab characters, etc. The following code
        # hacks around this behavior, which I consider to be a bug in Qt, by
        # (crudely) resetting the document's style state.
        cursor.movePosition(QtGui.QTextCursor.Left,
                            QtGui.QTextCursor.KeepAnchor)
        if cursor.selection().toPlainText() == ' ':
            cursor.removeSelectedText()
        else:
            cursor.movePosition(QtGui.QTextCursor.Right)
        cursor.insertText(' ', QtGui.QTextCharFormat())
        cursor.endEditBlock()

    # ConsoleWdiget
    @property
    def word_start_cursor(self):
        """ Start of the word to the left of the current text cursor. If a
            sequence of non-word characters precedes the first word, skip over
            them. (This emulates the behavior of bash, emacs, etc.)
        """
        cursor = self.textCursor()
        position = cursor.position()
        position -= 1
        while position >= 0 and not is_letter_or_number(self.document().characterAt(position)):
            position -= 1
        while position >= 0 and is_letter_or_number(self.document().characterAt(position)):
            position -= 1
        cursor.setPosition(position + 1)
        return cursor

    # ConsoleWidget
    @property
    def word_end_cursor(self):
        """ End of the word to the right the current text cursor. If a
            sequence of non-word characters precedes the first word, skip over
            them. (This emulates the behavior of bash, emacs, etc.)
        """
        cursor = self.textCursor()
        position = cursor.position()
        cursor.movePosition(QtGui.QTextCursor.End)
        end = cursor.position()
        while position < end and not is_letter_or_number(self.document().characterAt(position)):
            position += 1
        while position < end and is_letter_or_number(self.document().characterAt(position)):
            position += 1
        cursor = self.textCursor()
        cursor.setPosition(position)
        return cursor
