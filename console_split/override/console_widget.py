import sys
import re
from qtconsole.qt import QtCore, QtGui
from traitlets.config.configurable import LoggingConfigurable
from qtconsole.rich_text import HtmlExporter
from qtconsole.ansi_code_processor import QtAnsiCodeProcessor
from qtconsole.completion_widget import CompletionWidget
from qtconsole.completion_html import CompletionHtml
from qtconsole.completion_plain import CompletionPlain
from qtconsole.kill_ring import QtKillRing

from console_split.ui.text_area import RichOutArea, RichPageArea, RichInArea
from console_split.ui.signaller import Signaller

from console_split.modified_qtconsole.console_widget import ConsoleWidget
_ConsoleWidgetBase = ConsoleWidget

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def _create_view(font_family, gui_completion, control):
    #view = QtGui.QTextEdit()
    view = RichOutArea(font_family, gui_completion=gui_completion, input_target=control)
    #view.setFrameShape(QtGui.QFrame.StyledPanel)
    view.setReadOnly(True)

    return view


def console_widget_init(self, parent=None, **kw):
    """ Create a ConsoleWidget.

    Parameters
    ----------
    parent : QWidget, optional [default None]
        The parent for this widget.
    """
    QtGui.QWidget.__init__(self, parent)
    LoggingConfigurable.__init__(self, **kw)
    #self.paging = 'vsplit'
    # While scrolling the pager on Mac OS X, it tears badly.  The
    # NativeGesture is platform and perhaps build-specific hence
    # we take adequate precautions here.
    self._pager_scroll_events = [QtCore.QEvent.Wheel]
    if hasattr(QtCore.QEvent, 'NativeGesture'):
        self._pager_scroll_events.append(QtCore.QEvent.NativeGesture)

    # Create the layout and underlying text widget.
    layout = QtGui.QHBoxLayout(self)
    layout.setContentsMargins(0, 0, 0, 0)

    self._control = self._create_control()
    self._view = _create_view(self.font_family, self.gui_completion, self)

    view_stack = QtGui.QWidget()
    self.view_stack_layout = QtGui.QStackedLayout()
    view_stack.setLayout(self.view_stack_layout)
    self.view_stack_layout.addWidget(self._view)

    control_stack = QtGui.QWidget()
    self.control_stack_layout = QtGui.QStackedLayout()
    control_stack.setLayout(self.control_stack_layout)
    self.control_stack_layout.addWidget(self._control)

    self._main_splitter = QtGui.QSplitter()
    if self.paging == 'hsplit':
        self._main_splitter.setOrientation(QtCore.Qt.Horizontal)
    else:
        self._main_splitter.setOrientation(QtCore.Qt.Vertical)

    self._main_splitter.addWidget(view_stack)
    self._main_splitter.addWidget(control_stack)

    layout.addWidget(self._main_splitter)

    # Create the paging widget, if necessary.
    # TODO: 'vsplit' should open an extra area on the side of the control/view areas
    if self.paging in ('inside', 'hsplit', 'vsplit'):
        self._page_control = self._create_page_control()
        if self.paging == 'inside':
            self.control_stack_layout.addWidget(self._page_control)
        else:
            self.view_stack_layout.addWidget(self._page_control)

    # Initialize protected variables. Some variables contain useful state
    # information for subclasses; they should be considered read-only.
    self._append_before_prompt_pos = 0
    self._ansi_processor = QtAnsiCodeProcessor()
    if self.gui_completion == 'ncurses':
        self._completion_widget = CompletionHtml(self)
    elif self.gui_completion == 'droplist':
        self._completion_widget = CompletionWidget(self)
    elif self.gui_completion == 'plain':
        self._completion_widget = CompletionPlain(self)

    self._continuation_prompt = '> '
    self._continuation_prompt_html = None
    self._executing = False
    self._filter_resize = False
    self._html_exporter = HtmlExporter(self._control)
    self._input_buffer_executing = ''
    self._input_buffer_pending = ''
    self._kill_ring = QtKillRing(self._control)
    self._prompt = ''
    self._prompt_html = None
    self._prompt_pos = 0
    self._prompt_sep = ''
    self._reading = False
    self._reading_callback = None
    self._tab_width = 8

    # List of strings pending to be appended as plain text in the widget.
    # The text is not immediately inserted when available to not
    # choke the Qt event loop with paint events for the widget in
    # case of lots of output from kernel.
    self._pending_insert_text = []

    # Timer to flush the pending stream messages. The interval is adjusted
    # later based on actual time taken for flushing a screen (buffer_size)
    # of output text.
    self._pending_text_flush_interval = QtCore.QTimer(self._control)
    self._pending_text_flush_interval.setInterval(100)
    self._pending_text_flush_interval.setSingleShot(True)
    self._pending_text_flush_interval.timeout.connect(
            self._on_flush_pending_stream_timer)

    # Set a monospaced font.
    self.reset_font()

    # Configure actions.
    action = QtGui.QAction('Print', None)
    action.setEnabled(True)
    printkey = QtGui.QKeySequence(QtGui.QKeySequence.Print)
    if printkey.matches("Ctrl+P") and sys.platform != 'darwin':
        # Only override the default if there is a collision.
        # Qt ctrl = cmd on OSX, so the match gets a false positive on OSX.
        printkey = "Ctrl+Shift+P"
    action.setShortcut(printkey)
    action.setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)
    action.triggered.connect(self.print_)
    self.addAction(action)
    self.print_action = action

    action = QtGui.QAction('Save as HTML/XML', None)
    action.setShortcut(QtGui.QKeySequence.Save)
    action.setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)
    action.triggered.connect(self.export_html)
    self.addAction(action)
    self.export_action = action

    action = QtGui.QAction('Select All', None)
    action.setEnabled(True)
    selectall = QtGui.QKeySequence(QtGui.QKeySequence.SelectAll)
    if selectall.matches("Ctrl+A") and sys.platform != 'darwin':
        # Only override the default if there is a collision.
        # Qt ctrl = cmd on OSX, so the match gets a false positive on OSX.
        selectall = "Ctrl+Shift+A"
    action.setShortcut(selectall)
    action.setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)
    action.triggered.connect(self.select_all)
    self.addAction(action)
    self.select_all_action = action

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

    # Accept drag and drop events here. Drops were already turned off
    # in self._control when that widget was created.
    self.setAcceptDrops(True)


_ConsoleWidgetBase.__init__ = console_widget_init


class ConsoleWidget(_ConsoleWidgetBase):
    signaller = None

    def __init__(self, *args, **kw):
        super(ConsoleWidget, self).__init__(*args, **kw)
        self.signaller = Signaller()
        #Connect output slot
        self.signaller.connect_signal(self._view.insert_signal_content)
        #print('init overriden ConsoleWidget')

    def _create_control(self):
        """ Creates and connects the underlying text widget.
        """
        # Create the underlying control.
        if self.kind == 'plain':
            control = QtGui.QPlainTextEdit()
        else:
            control = RichInArea(self.font_family, self.gui_completion)

        # Install event filters. The filter on the viewport is needed for
        # mouse events.
        control.installEventFilter(self)
        control.viewport().installEventFilter(self)

        return control

    def _set_paging(self, paging):
        """
        Change the pager to `paging` style.

        Parameters
        ----------
        paging : string
            Either "hsplit", "vsplit", or "inside"
        """
        if paging == 'hsplit':
            self._main_splitter.setOrientation(QtCore.Qt.Horizontal)
        elif paging == 'vsplit':
            self._main_splitter.setOrientation(QtCore.Qt.Vertical)
        elif paging == 'inside':
            self._main_splitter.setOrientation(QtCore.Qt.Horizontal)
        elif paging == 'none':
            pass
        else:
            raise ValueError("unknown paging method '%s'" % paging)
        self.paging = paging

    def _page(self, text, html=False):
        """ Displays text using the pager if it exceeds the height of the
        viewport.

        Parameters
        ----------
        html : bool, optional (default False)
            If set, the text will be interpreted as HTML instead of plain text.
        """
        line_height = QtGui.QFontMetrics(self.font).height()
        min_lines = self._control.viewport().height() / line_height
        if self.paging != 'none' and \
                re.match("(?:[^\n]*\n){%i}" % min_lines, text):
            if self.paging == 'custom':
                self.custom_page_requested.emit(text)
            else:
                # disable buffer truncation during paging
                self._control.document().setMaximumBlockCount(0)
                self._page_control.clear()
                cursor = self._page_control.textCursor()
                if html:
                    self._insert_html(cursor, text)
                else:
                    self._insert_plain_text(cursor, text)
                self._page_control.moveCursor(QtGui.QTextCursor.Start)

                self._page_control.viewport().resize(self._control.size())

                if self.paging == 'inside':
                    #print('set control')
                    self.control_stack_layout.setCurrentWidget(self._page_control)
                else:
                    #print('set view')
                    self.view_stack_layout.setCurrentWidget(self._page_control)

        elif html:
            self._append_html(text)
        else:
            self._append_plain_text(text)

    def _event_filter_page_keypress(self, event):
        """ Filter key events for the paging widget to create console-like
            interface.
        """
        key = event.key()
        ctrl_down = self._control_key_down(event.modifiers())
        alt_down = event.modifiers() & QtCore.Qt.AltModifier

        if ctrl_down:
            if key == QtCore.Qt.Key_O:
                self._control.setFocus()
                intercept = True

        elif alt_down:
            if key == QtCore.Qt.Key_Greater:
                self._page_control.moveCursor(QtGui.QTextCursor.End)
                intercepted = True

            elif key == QtCore.Qt.Key_Less:
                self._page_control.moveCursor(QtGui.QTextCursor.Start)
                intercepted = True

        elif key in (QtCore.Qt.Key_Q, QtCore.Qt.Key_Escape):
            if self.paging == 'inside':
                #print('reset control')
                self.control_stack_layout.setCurrentWidget(self._control)
            else:
                #print('reset view')
                self.view_stack_layout.setCurrentWidget(self._view)
            # re-enable buffer truncation after paging
            self._control.document().setMaximumBlockCount(self.buffer_size)
            return True

        elif key in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return,
                     QtCore.Qt.Key_Tab):
            new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                        QtCore.Qt.Key_PageDown,
                                        QtCore.Qt.NoModifier)
            QtGui.qApp.sendEvent(self._page_control, new_event)
            return True

        elif key == QtCore.Qt.Key_Backspace:
            new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                        QtCore.Qt.Key_PageUp,
                                        QtCore.Qt.NoModifier)
            QtGui.qApp.sendEvent(self._page_control, new_event)
            return True

        # vi/less -like key bindings
        elif key == QtCore.Qt.Key_J:
            new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                        QtCore.Qt.Key_Down,
                                        QtCore.Qt.NoModifier)
            QtGui.qApp.sendEvent(self._page_control, new_event)
            return True

        # vi/less -like key bindings
        elif key == QtCore.Qt.Key_K:
            new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                        QtCore.Qt.Key_Up,
                                        QtCore.Qt.NoModifier)
            QtGui.qApp.sendEvent(self._page_control, new_event)
            return True
        return False

    def _create_page_control(self):
        """ Creates and connects the underlying paging widget.
        """
        if self.custom_page_control:
            control = self.custom_page_control()
        elif self.kind == 'plain':
            control = QtGui.QPlainTextEdit()
        elif self.kind == 'rich':
            control = RichPageArea(self.font_family, self._view)
        control.installEventFilter(self)
        viewport = control.viewport()
        viewport.installEventFilter(self)
        control.setReadOnly(True)
        control.setUndoRedoEnabled(False)
        control.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        return control
