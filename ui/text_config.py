import sys
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


# ConsoleWidget
def _get_block_plain_text(block):
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
        string = _get_block_plain_text(current_block)

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

    _ansi_processor = None  # QtAnsiCodeProcessor

    def __init__(self, **kwargs):
        """
        Initialize.
        :return:
        """
        super(LoggingConfigurable, self).__init__(**kwargs)
        self._ansi_processor = QtAnsiCodeProcessor()

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
        self._ansi_processor.set_background_color(bg_color)

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
