import sys
from functools import singledispatch
#from traitlets import Bool
from qtconsole.util import get_font
from qtconsole.qt import QtCore
from qtconsole.rich_text import HtmlExporter
from qtconsole.qt import QtGui
from qtconsole.console_widget import ConsoleWidget
from qtconsole.ansi_code_processor import QtAnsiCodeProcessor
from qtconsole.completion_widget import CompletionWidget
from qtconsole.completion_html import CompletionHtml
from qtconsole.completion_plain import CompletionPlain

from console_split.ui.signal_content import TextSignal, HtmlSignal
from .context_menu import ContextMenu

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def _set_top_cursor(target, cursor):
    """ Scrolls the viewport so that the specified cursor is at the top of target.
    """
    scrollbar = target.verticalScrollBar()
    #print('page step: ' + str(scrollbar.pageStep()))
    scrollbar.setValue(scrollbar.maximum())
    original_cursor = target.textCursor()
    target.setTextCursor(cursor)
    target.ensureCursorVisible()
    target.setTextCursor(original_cursor)


def _control_key_down(modifiers, include_command=False):
    """ Given a KeyboardModifiers flags object, return whether the Control
    key is down.

    Parameters
    ----------
    include_command : bool, optional (default True)
        Whether to treat the Command key as a (mutually exclusive) synonym
        for Control when in Mac OS.
    """
    # Note that on Mac OS, ControlModifier corresponds to the Command key
    # while MetaModifier corresponds to the Control key.
    if sys.platform == 'darwin':
        down = include_command and (modifiers & QtCore.Qt.ControlModifier)
        return bool(down) ^ bool(modifiers & QtCore.Qt.MetaModifier)
    else:
        return bool(modifiers & QtCore.Qt.ControlModifier)


@singledispatch
def post_signal_content(output, target, ansi_processor):
    raise NotImplementedError


@post_signal_content.register(TextSignal)
def _(output, target, ansi_processor):
    if output.message:
        cursor = target.textCursor()
        text = output.message
        # adopted from qtconsole.console_widget._insert_plain_text(self, cursor, text, flush=False)
        cursor.beginEditBlock()
        if output.ansi_codes:
            #print('do ansi')
            for substring in ansi_processor.split_string(text):
                for act in ansi_processor.actions:
                    #print(act)

                    # Unlike real terminal emulators, we don't distinguish
                    # between the screen and the scrollback buffer. A screen
                    # erase request clears everything.
                    if act.action == 'erase' and act.area == 'screen':
                        cursor.select(QtGui.QTextCursor.Document)
                        cursor.removeSelectedText()

                    # Simulate a form feed by scrolling just past the last line.
                    elif act.action == 'scroll' and act.unit == 'page':
                        #print('do page scroll')
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

                out_format = ansi_processor.get_format()

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


@post_signal_content.register(HtmlSignal)
def _(output, target, ansi_processor):
    if output.message:
        #target.insertHtml(output.content)
        #print(type(target))
        ConsoleWidget._insert_html(None, target.textCursor(), output.message)


class AnyTextMixin(object):
    input_target = None

    ansi_processor = None
    html_exporter = None
    #gui_completion = ''
    completion_widget = None
    font_family = None
    font_size = None
    _tab_width = 8

    # indicate whether resizing is currently be processed by eventFilter
    _filter_resize = False
    # When the control key is down, these keys are mapped.
    _ctrl_down_remap = { QtCore.Qt.Key_B : QtCore.Qt.Key_Left,
                         QtCore.Qt.Key_F : QtCore.Qt.Key_Right,
                         QtCore.Qt.Key_A : QtCore.Qt.Key_Home,
                         QtCore.Qt.Key_P : QtCore.Qt.Key_Up,
                         QtCore.Qt.Key_N : QtCore.Qt.Key_Down,
                         QtCore.Qt.Key_H : QtCore.Qt.Key_Backspace, }
    if not sys.platform == 'darwin':
        # On OS X, Ctrl-E already does the right thing, whereas End moves the
        # cursor to the bottom of the buffer.
        _ctrl_down_remap[QtCore.Qt.Key_E] = QtCore.Qt.Key_End

    # Whether to override ShortcutEvents for the keybindings defined by this
    # widget (Ctrl+n, Ctrl+a, etc). Enable this if you want this widget to take
    # priority (when it has focus) over, e.g., window-level menu shortcuts.
    override_shortcuts = False  # Bool(False)

    # The shortcuts defined by this widget. We need to keep track of these to
    # support 'override_shortcuts' above.
    _shortcuts = set(_ctrl_down_remap.keys()) | \
                     { QtCore.Qt.Key_C, QtCore.Qt.Key_G, QtCore.Qt.Key_O,
                       QtCore.Qt.Key_V }

    def __init__(self, font_family, gui_completion='', input_target=None):
        self._filter_resize = False

        self.font_family = font_family
        self.input_target = input_target if input_target else self

        self.ansi_processor = QtAnsiCodeProcessor()
        self.html_exporter = HtmlExporter(self)

        # Completion* classes need to be fixed to work here
        # self._control = self
        # if gui_completion == 'ncurses':
        #     self._completion_widget = CompletionHtml(self)
        # elif gui_completion == 'droplist':
        #     self._completion_widget = CompletionWidget(self)
        # elif gui_completion == 'plain':
        #     self._completion_widget = CompletionPlain(self)

        # Hijack the document size change signal to prevent Qt from adjusting
        # the viewport's scrollbar. We are relying on an implementation detail
        # of Q(Plain)TextEdit here, which is potentially dangerous, but without
        # this functionality we cannot create a nice terminal interface.
        layout = self.document().documentLayout()
        layout.documentSizeChanged.disconnect()
        layout.documentSizeChanged.connect(self._adjust_scrollbars())

        if self.input_target==self:
            self.setAcceptDrops(True)
        else:
            self.setAcceptDrops(False)
        self.reset_font()

        # Actions
        action = QtGui.QAction('Select All', None)
        action.setEnabled(True)
        select_all_keys = QtGui.QKeySequence(QtGui.QKeySequence.SelectAll)
        if select_all_keys.matches("Ctrl+A") and sys.platform != 'darwin':
            # Only override the default if there is a collision.
            # Qt ctrl = cmd on OSX, so the match gets a false positive on OSX.
            select_all_keys = "Ctrl+Shift+A"
        action.setShortcut(select_all_keys)
        action.setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)
        action.triggered.connect(self.selectAll)
        self.addAction(action)
        self.select_all_action = action

        # Export action
        action = QtGui.QAction('Save as HTML/XML', None)
        action.setShortcut(QtGui.QKeySequence.Save)
        action.setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)
        action.triggered.connect(self.html_exporter.export)
        self.addAction(action)
        self.export_action = action

        action = QtGui.QAction('Print', None)
        action.setEnabled(True)
        print_key = QtGui.QKeySequence(QtGui.QKeySequence.Print)
        if print_key.matches("Ctrl+P") and sys.platform != 'darwin':
            # Only override the default if there is a collision.
            # Qt ctrl = cmd on OSX, so the match gets a false positive on OSX.
            print_key = "Ctrl+Shift+P"
        action.setShortcut(print_key)
        action.setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)
        action.triggered.connect(self.print_)
        self.addAction(action)
        self.print_action = action

        self.increase_font_size = QtGui.QAction("Bigger Font",
                self,
                shortcut=QtGui.QKeySequence.ZoomIn,
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

        # Connect signals.
        self.customContextMenuRequested.connect(self._custom_context_menu_requested)
        self.copyAvailable.connect(self.copy_available)
        self.redoAvailable.connect(self.redo_available)
        self.undoAvailable.connect(self.undo_available)

        self.setAttribute(QtCore.Qt.WA_InputMethodEnabled, True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setReadOnly(True)
        self.setUndoRedoEnabled(False)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

    #########################################################################################################

    def _get_font(self):
        """ The base font being used by the ConsoleWidget.
        """
        return self.document().defaultFont()

    def _set_font(self, font):
        """ Sets the base font for the ConsoleWidget to the specified QFont.
        """
        font_metrics = QtGui.QFontMetrics(font)
        self.setTabStopWidth(self.tab_width * font_metrics.width(' '))

        if self.completion_widget:
            self._completion_widget.setFont(font)
        self.document().setDefaultFont(font)
        #do not need beause pager will be TextArea with its own actions
        #if self._page_control:
        #    self._page_control.document().setDefaultFont(font)

        self.font_changed.emit(font)

    font = property(_get_font, _set_font)

    def _get_tab_width(self):
        """ The width (in terms of space characters) for tab characters.
        """
        return self._tab_width

    def _set_tab_width(self, tab_width):
        """ Sets the width (in terms of space characters) for tab characters.
        """
        font_metrics = QtGui.QFontMetrics(self.font)
        self._control.setTabStopWidth(tab_width * font_metrics.width(' '))

        self._tab_width = tab_width

    tab_width = property(_get_tab_width, _set_tab_width)

    def reset_font(self):
        """ Sets the font to the default fixed-width font for this platform.
        """
        if sys.platform == 'win32':
            # Consolas ships with Vista/Win7, fallback to Courier if needed
            fallback = 'Courier'
        elif sys.platform == 'darwin':
            # OSX always has Monaco
            fallback = 'Monaco'
        else:
            # Monospace should always exist
            fallback = 'Monospace'
        font = get_font(self.font_family, fallback)
        if self.font_size:
            font.setPointSize(self.font_size)
        else:
            font.setPointSize(QtGui.qApp.font().pointSize())
        font.setStyleHint(QtGui.QFont.TypeWriter)
        self._set_font(font)

    def change_font_size(self, delta):
        """Change the font size by the specified amount (in points).
        """
        font = self.font
        size = max(font.pointSize() + delta, 1) # minimum 1 point
        font.setPointSize(size)
        self._set_font(font)

    def _increase_font_size(self):
        self.change_font_size(1)

    def _decrease_font_size(self):
        self.change_font_size(-1)

    def print_(self, printer=None):
        """ Print the contents of the ConsoleWidget to the specified QPrinter.
        """
        if (not printer):
            printer = QtGui.QPrinter()
            if(QtGui.QPrintDialog(printer).exec_() != QtGui.QDialog.Accepted):
                return
        self.print_(printer)

    def can_copy(self):
        """ Returns whether text can be copied to the clipboard.
        """
        return self.textCursor().hasSelection()

    def can_cut(self):
        """ Returns whether text can be cut to the clipboard.
        """
        cursor = self.textCursor()
        return (cursor.hasSelection() and
                self._in_buffer(cursor.anchor()) and
                self._in_buffer(cursor.position()))

    def can_paste(self):
        """ Returns whether text can be pasted from the clipboard.
        """
        if self.textInteractionFlags() & QtCore.Qt.TextEditable:
            return bool(QtGui.QApplication.clipboard().text())
        return False


    #---------------------------------------------------------------------------
    # Drag and drop support
    #---------------------------------------------------------------------------

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            # The link action should indicate to that the drop will insert
            # the file anme.
            e.setDropAction(QtCore.Qt.LinkAction)
            e.accept()
        elif e.mimeData().hasText():
            # By changing the action to copy we don't need to worry about
            # the user accidentally moving text around in the widget.
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls():
            pass
        elif e.mimeData().hasText():
            cursor = self.cursorForPosition(e.pos())
            if self._in_buffer(cursor.position()):
                e.setDropAction(QtCore.Qt.CopyAction)
                self.setTextCursor(cursor)
            else:
                e.setDropAction(QtCore.Qt.IgnoreAction)
            e.accept()

    def dropEvent(self, e):
        if e.mimeData().hasUrls():
            self._keep_cursor_in_buffer()
            cursor = self.textCursor()
            filenames = [url.toLocalFile() for url in e.mimeData().urls()]
            text = ', '.join("'" + f.replace("'", "'\"'\"'") + "'"
                             for f in filenames)
            self._insert_plain_text_into_buffer(cursor, text)
        elif e.mimeData().hasText():
            cursor = self.cursorForPosition(e.pos())
            if self._in_buffer(cursor.position()):
                text = e.mimeData().text()
                self._insert_plain_text_into_buffer(cursor, text)

    # Signal handlers ----------------------------------------------------
    def _custom_context_menu_requested(self, pos):
        """ Shows a context menu at the given QPoint (in widget coordinates).
        """
        menu = self.make_context_menu(pos)
        menu.exec_(self.mapToGlobal(pos))

    def _adjust_scrollbars(self):
        """ Expands the vertical scrollbar beyond the range set by Qt.
        """
        # This code is adapted from _q_adjustScrollbars in qplaintextedit.cpp
        # and qtextedit.cpp.
        def _adjust_scrollbars_fun():
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
        return _adjust_scrollbars_fun
