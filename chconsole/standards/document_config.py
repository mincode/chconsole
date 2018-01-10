import os
import re
import sys
import webbrowser

from ipython_genutils import py3compat
from ipython_genutils.importstring import import_item
from ipython_genutils.path import ensure_dir_exists
from qtconsole import styles
from qtconsole.ansi_code_processor import QtAnsiCodeProcessor
from qtconsole.qt import QtGui, QtCore
from qtconsole.rich_text import HtmlExporter
from qtconsole.util import get_font
from traitlets import Integer, Unicode, DottedObjectName, Any, Float, Instance
from traitlets.config.configurable import LoggingConfigurable

from chconsole.media import (set_top_cursor, insert_qimage_format,
                             is_letter_or_number)
from chconsole.menus import TextContextMenu, ImageContextMenu
from .selective_highlighter import SelectiveHighlighter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


code_active_color = QtCore.Qt.black  # color used for widget's frame if in code mode
chat_active_color = QtCore.Qt.red  # color used for the widget's frame if in chat mode


class DocumentConfig(LoggingConfigurable):
    """
    Mixin for configuring text properties of a subclass of an editor class, QTextEdit or QPlainTextEdit.
    It should be initialized after the editor class has been initialized.
    """
    highlighter = Instance(SelectiveHighlighter, allow_none=True)

    font_family = Unicode(
        config=True,
        help="""The font family to use for the console.
        On OSX this defaults to Monaco, on Windows the default is
        Consolas with fallback of Courier, and on other platforms
        the default is Monospace.
        """)

    font_size = Integer(
        config=True, help="The font size. If unconfigured, Qt will be entrusted with the size of the font.")

    standard_tab_width = Integer(4, config=True, help="Number of spaces used for tab.")

    style_sheet = Unicode(config=False,
        help="""
        A CSS stylesheet. The stylesheet can contain classes for:
            1. Qt: QPlainTextEdit, QFrame, QWidget, etc
            2. Pygments: .c, .k, .o, etc. (see PygmentsHighlighter)
            3. ChatConsole: .error, .in-prompt, .out-prompt, etc
        """)

    syntax_style = Unicode(config=False,
        help="""
        If not empty, use this Pygments style for syntax highlighting.
        Otherwise, the style sheet is queried for Pygments style
        information.
        """)

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

    html_exporter = None
    print_action = None  # action for printing
    export_action = None  # action for exporting
    select_all_action = None  # action for selecting all

    use_ansi = True  # whether to use ansi codes in text
    name_to_svg_map = None  # Dictionary for resolving document resource names to SVG data.

    # RichJupyterWidget:
    # Used to determine whether a given html export attempt has already
    # displayed a warning about being unable to convert a png to svg.
    svg_warning = None  # QSemaphore(0)

    def __init__(self, use_ansi=True, **kwargs):
        """
        Initialize.
        :return:
        """
        super(LoggingConfigurable, self).__init__(**kwargs)

        # Text interaction
        self.name_to_svg_map = {}
        self.svg_warning = QtCore.QSemaphore()
        self.highlighter = SelectiveHighlighter(self, lexer=self.lexer)
        self.use_ansi = use_ansi
        self.setMouseTracking(True)
        if hasattr(self, 'setAcceptRichText'):
            self.setAcceptRichText(False)

        self.setAttribute(QtCore.Qt.WA_InputMethodEnabled, True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setReadOnly(False)
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

        action = QtGui.QAction('Print', None)
        action.setEnabled(True)
        print_key = QtGui.QKeySequence(QtGui.QKeySequence.Print)
        if print_key.matches("Ctrl+P") and sys.platform != 'darwin':
            # Only override the default if there is a collision.
            # Qt ctrl = cmd on OSX, so the match gets a false positive on OSX.
            print_key = "Ctrl+Shift+P"
        action.setShortcut(print_key)
        action.setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)
        action.triggered.connect(self._print_doc)
        self.addAction(action)
        self.print_action = action

        self.html_exporter = HtmlExporter(self)
        if isinstance(self, QtGui.QTextEdit):
            self.html_exporter.image_tag = self.get_image_tag
        action = QtGui.QAction('Save as HTML/XML', None)
        action.setShortcut(QtGui.QKeySequence.Save)
        action.setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)
        action.triggered.connect(self.html_exporter.export)
        self.addAction(action)
        self.export_action = action

        action = QtGui.QAction('Select All', None)
        action.setEnabled(True)
        select_all = QtGui.QKeySequence(QtGui.QKeySequence.SelectAll)
        if select_all.matches("Ctrl+A") and sys.platform != 'darwin':
            # Only override the default if there is a collision.
            # Qt ctrl = cmd on OSX, so the match gets a false positive on OSX.
            select_all = "Ctrl+Shift+A"
        action.setShortcut(select_all)
        action.setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)
        action.triggered.connect(self.selectAll)
        self.addAction(action)
        self.select_all_action = action

        # Set a monospaced font.
        self.reset_font()

        # Context menu
        self.customContextMenuRequested.connect(
            self._custom_context_menu_requested)

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
        self.set_font(font)

    def get_font(self):
        """ The base font being used.
        """
        return self.document().defaultFont()

    def set_font(self, font):
        """ Sets the base font for the ConsoleWidget to the specified QFont.
        """
        font_metrics = QtGui.QFontMetrics(font)
        self.setTabStopWidth(self.tab_width * font_metrics.width(' '))

        self.document().setDefaultFont(font)

    font = property(get_font, set_font)

    def change_font_size(self, delta):
        """Change the font size by the specified amount (in points).
        """
        font = self.font
        size = max(font.pointSize() + delta, 1)  # minimum 1 point
        font.setPointSize(size)
        self.set_font(font)

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

    def set_frame_color(self, new_color):
        """
        Set the frame color according.
        :param new_color color to set.
        :return:
        """
        new_palette = self.palette()
        # new_palette.setColor(QtGui.QPalette.WindowText, new_color)
        new_palette.setColor(QtGui.QPalette.Window, new_color)
        self.setPalette(new_palette)

    # traitlets

    # JupyterWidget
    def _style_sheet_changed(self):
        """ Set the style sheets of the underlying widgets.
        """
        self.setStyleSheet(self.style_sheet)
        self.document().setDefaultStyleSheet(self.style_sheet)
        # bg_color = self.palette().window().color()
        bg_color = 'default'
        self.ansi_processor.set_background_color(bg_color)

        # if self._page_control is not None:
        #     self._page_control.document().setDefaultStyleSheet(self.style_sheet)

    # JupyterWidget
    def _syntax_style_changed(self):
        """ Set the style for the syntax highlighter.
        """
        if self.highlighter is None:
            # ignore premature calls
            return
        if self.syntax_style:
            self.highlighter.set_style(self.syntax_style)
        else:
            self.highlighter.set_style_sheet(self.style_sheet)

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

    # ConsoleWidget
    def copy_anchor(self, anchor):
        """ Copy anchor text to the clipboard
        """
        QtGui.QApplication.clipboard().setText(anchor)

    # ConsoleWidget
    def open_anchor(self, anchor):
        """ Open selected anchor in the default webbrowser
        """
        webbrowser.open(anchor)

    @property
    def end_cursor(self):
        """
        Return a text cursor at the end of the document.
        :param target: target editor object to get the cursor.
        :return: text cursor at the end of target.
        """
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        return cursor

    def insert_qimage(self, image_format, cursor=None):
        cursor = cursor if cursor else self.textCursor()
        insert_qimage_format(cursor, image_format)

    # RichJupyterWidget
    # orig: _get_image, _get_image_tag
    def get_image(self, name):
        """ Returns the QImage stored as the ImageResource with 'name'.
        """
        document = self.document()
        image = document.resource(QtGui.QTextDocument.ImageResource,
                                  QtCore.QUrl(name))
        return image

    def get_image_tag(self, match, path = None, format = "png"):
        """ Return (X)HTML mark-up for the image-tag given by match.

        Parameters
        ----------
        match : re.SRE_Match
            A match to an HTML image tag as exported by Qt, with
            match.group("Name") containing the matched image ID.

        path : string|None, optional [default None]
            If not None, specifies a path to which supporting files may be
            written (e.g., for linked images).  If None, all images are to be
            included inline.

        format : "png"|"svg"|"jpg", optional [default "png"]
            Format for returned or referenced images.
        """
        if format in ("png","jpg"):
            try:
                image = self.get_image(match.group("name"))
            except KeyError:
                return "<b>Couldn't find image %s</b>" % match.group("name")

            if path is not None:
                ensure_dir_exists(path)
                rel_path = os.path.basename(path)
                if image.save("%s/qt_img%s.%s" % (path, match.group("name"), format),
                              "PNG"):
                    return '<img src="%s/qt_img%s.%s">' % (rel_path, match.group("name"),format)
                else:
                    return "<b>Couldn't save image!</b>"
            else:
                ba = QtCore.QByteArray()
                buffer_ = QtCore.QBuffer(ba)
                buffer_.open(QtCore.QIODevice.WriteOnly)
                image.save(buffer_, format.upper())
                buffer_.close()
                return '<img src="data:image/%s;base64,\n%s\n" />' % (
                    format,re.sub(r'(.{60})',r'\1\n',str(ba.toBase64())))

        elif format == "svg":
            try:
                svg = str(self.name_to_svg_map[match.group("name")])
            except KeyError:
                if self.svg_warning.tryAcquire():
                    QtGui.QMessageBox.warning(self, 'Error converting PNG to SVG.',
                        'Cannot convert PNG images to SVG, export with PNG figures instead. '
                        'If you want to export matplotlib figures as SVG, add '
                        'to your ipython config:\n\n'
                        '\tc.InlineBackend.figure_format = \'svg\'\n\n'
                        'And regenerate the figures.',
                                              QtGui.QMessageBox.Ok)
                return ("<b>Cannot convert  PNG images to SVG.</b>  "
                        "You must export this session with PNG images. "
                        "If you want to export matplotlib figures as SVG, add to your config "
                        "<span>c.InlineBackend.figure_format = 'svg'</span> "
                        "and regenerate the figures.")

            # Not currently checking path, because it's tricky to find a
            # cross-browser way to embed external SVG images (e.g., via
            # object or embed tags).

            # Chop stand-alone header from matplotlib SVG
            offset = svg.find("<svg")
            assert(offset > -1)

            return svg[offset:]

        else:
            return '<b>Unrecognized image format</b>'


    # adopted from ConsoleWidget
    def insert_ansi_text(self, text, ansi_codes=True, cursor=None):
        cursor = cursor if cursor else self.textCursor()
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
                        # cursor.endEditBlock()
                        set_top_cursor(self, cursor)
                        # cursor.joinPreviousEditBlock()
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

    # ConsoleWidget
    def can_copy(self):
        """ Returns whether text can be copied to the clipboard.
        """
        return self.textCursor().hasSelection()

    # ConsoleWidget
    def can_cut(self):
        """ Returns whether text can be cut to the clipboard.
        """
        if not self.isReadOnly():
            return self.textCursor().hasSelection()

    # ConsoleWidget
    def can_paste(self):
        """ Returns whether text can be pasted from the clipboard.
        """
        paste_able = False
        if not self.isReadOnly():
            paste_able = bool(QtGui.QApplication.clipboard().text())
        return paste_able

    # ConsoleWidget
    def export_html(self):
        """ Shows a dialog to export HTML/XML in various formats.
        """
        self.svg_warning.tryAcquire()  # svg_warning can be 0 or 1.
        self.svg_warning.release()  # svg warning should be 1 before export.
        self.html_exporter.export()

    # ConsoleWidget
    def _print_doc(self, printer=None):
        """ Print the contents of the ConsoleWidget to the specified QPrinter.
        """
        if not printer:
            printer = QtGui.QPrinter()
            if QtGui.QPrintDialog(printer).exec_() != QtGui.QDialog.Accepted:
                return
        self.print_(printer)

    # ConsoleWidget
    def _custom_context_menu_requested(self, pos):
        """ Shows a context menu at the given QPoint (in widget coordinates).
        """
        char_format = self.cursorForPosition(pos).charFormat()
        name = char_format.stringProperty(QtGui.QTextFormat.ImageName)
        if name:
            menu = ImageContextMenu(self, pos, name)
        else:
            menu = TextContextMenu(self, pos)
        menu.exec_(self.mapToGlobal(pos))
