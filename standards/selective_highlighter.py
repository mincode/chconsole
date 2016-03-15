from qtconsole.pygments_highlighter import PygmentsHighlighter
from media import get_block_plain_text

__author__ = 'Manfred Minimair <manfred@minimair.org>'


# based on FrontendHighlighter of FrontendWidget
class SelectiveHighlighter(PygmentsHighlighter):
    """ A PygmentsHighlighter that ignores prompts and can be used selectively.
    """
    _editor = None  # QTextEdit or QPlainTextEdit
    _highlighting_on = False  # whether to highlight
    _current_offset = 0  # offset to skip prompt

    def __init__(self, editor, lexer=None):
        """
        Initialize to be disabled by default.
        :param editor: QTextEdit or QPlainTextEdit.
        :param lexer: lexer used for highlighting.
        :return:
        """
        super(SelectiveHighlighter, self).__init__(editor.document(), lexer=lexer)
        self._editor = editor

    def enable(self, offset=0):
        """
        Enable highlighting.
        :param offset: Highlight current block starting with offset position
        (position of the start of the block + offset).
        :return:
        """
        self._current_offset = offset
        self. _highlighting_on = True

    def disable(self):
        """
        Disable highlighting and reset offset to zero.
        :return:
        """
        self._highlighting_on = False
        self._current_offset = 0

    def highlightBlock(self, string):
        """ Highlight a block of text. Reimplemented to highlight selectively.
        """
        if self._highlighting_on:
            self._current_offset = 0
            # The input to this function is a unicode string that may contain
            # paragraph break characters, non-breaking spaces, etc. Here we acquire
            # the string as plain text so we can compare it.
            current_block = self.currentBlock()
            string = get_block_plain_text(current_block)
            super(SelectiveHighlighter, self).highlightBlock(string[self._current_offset:])

    def rehighlightBlock(self, block):
        """ Reimplemented to temporarily enable highlighting if disabled.
        """
        old = self._highlighting_on
        self._highlighting_on = True
        super(SelectiveHighlighter, self).rehighlightBlock(block)
        self._highlighting_on = old

    def setFormat(self, start, count, format):
        """ Reimplemented to highlight selectively.
        """
        start += self._current_offset
        super(SelectiveHighlighter, self).setFormat(start, count, format)
