from qtconsole.qt import QtGui, QtCore
from .any_text_mixin import AnyTextMixin, post_signal_content
from .rich_text_mixin import RichTextMixin
from .signal_content import SignalContent
from .plain_out_mixin import PlainOutMixin
from .plain_page_mixin import PlainPageMixin

__author__ = 'Manfred Minimair <manfred@minimair.org>'



# EDITOR is either QtGui.QTextEdit or QtGui.QPlainTextEdit
# Use _AnyTextArea with QtGui.QPlainTextEdit as PlainTextArea
class _AnyTextArea(AnyTextMixin, EDITOR):
    # Signals that indicate ConsoleWidget state.
    copy_available = QtCore.Signal(bool)
    redo_available = QtCore.Signal(bool)  # so far not supported
    undo_available = QtCore.Signal(bool)  # so far not supported
    # Signal emitted when the font is changed.
    font_changed = QtCore.Signal(QtGui.QFont)

    def __init__(self, font_family, gui_completion, input_target, parent):
        EDITOR.__init__(self, parent)
        AnyTextMixin.__init__(self, font_family, gui_completion, input_target)

    @QtCore.Slot(SignalContent)
    def insert_signal_content(self, output):
        post_signal_content(output, self, self.ansi_processor)

    # --- Events
    def eventFilter(self, obj, event):
        """ Reimplemented to ensure a console-like behavior in the underlying
            text widgets.
        """
        event_type = event.type()
        if event_type == QtCore.QEvent.KeyPress:

            # Re-map keys for all filtered widgets.
            key = event.key()
            if self._control_key_down(event.modifiers()) and \
                    key in self._ctrl_down_remap:
                new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                            self._ctrl_down_remap[key],
                                            QtCore.Qt.NoModifier)
                QtGui.qApp.sendEvent(obj, new_event)
                return True

            elif obj == self._control:
                return self._event_filter_console_keypress(event)

            elif obj == self._page_control:
                return self._event_filter_page_keypress(event)

# subclass
        # # Make middle-click paste safe.
        # elif event_type == QtCore.QEvent.MouseButtonRelease and \
        #         event.button() == QtCore.Qt.MidButton and \
        #         obj == self._control.viewport():
        #     cursor = self._control.cursorForPosition(event.pos())
        #     self._control.setTextCursor(cursor)
        #     self.paste(QtGui.QClipboard.Selection)
        #     return True

# OK
        # Manually adjust the scrollbars *after* a resize event is dispatched.
        elif event_type == QtCore.QEvent.Resize and not self._filter_resize:
            self._filter_resize = True
            QtGui.qApp.sendEvent(obj, event)
            self._adjust_scrollbars()
            self._filter_resize = False
            return True
# OK
        # Override shortcuts for all filtered widgets.
        elif event_type == QtCore.QEvent.ShortcutOverride and \
                self.override_shortcuts and \
                self._control_key_down(event.modifiers()) and \
                event.key() in self._shortcuts:
            event.accept()

# Later
#         # Handle scrolling of the vsplit pager. This hack attempts to solve
#         # problems with tearing of the help text inside the pager window.  This
#         # happens only on Mac OS X with both PySide and PyQt. This fix isn't
#         # perfect but makes the pager more usable.
#         elif event_type in self._pager_scroll_events and \
#                 obj == self._page_control:
#             self._page_control.repaint()
#             return True

# OK
        elif event_type == QtCore.QEvent.MouseMove:
            anchor = self.anchorAt(event.pos())
            QtGui.QToolTip.showText(event.globalPos(), anchor)

        return super(_AnyTextArea, self).eventFilter(obj, event)


class PlainOutArea(PlainOutMixin, _AnyTextArea):
    def __init__(self, font_family, gui_completion, input_target, parent):
        _AnyTextArea.__init__(self, font_family, gui_completion, input_target, parent)


class RichOutArea(RichTextMixin, PlainOutArea):
    def __init__(self, font_family, gui_completion='', input_target=None, parent=None):
        _AnyTextArea.__init__(self, font_family, gui_completion, input_target, parent)
        RichTextMixin.__init__(self)


class PlainPageArea(PlainPageMixin, _AnyTextArea):
    def __init__(self, font_family, input_target, parent):
        _AnyTextArea.__init__(self, font_family, input_target, parent)


class RichPageArea(RichTextMixin, PlainPageArea):
    def __init__(self, font_family, input_target, parent=None):
        _AnyTextArea.__init__(self, font_family, '', input_target, parent)
        RichTextMixin.__init__(self)


class RichInArea(RichTextMixin, PlainOutArea):
    def __init__(self, font_family, gui_completion='', parent=None):
        _AnyTextArea.__init__(self, font_family, gui_completion, self, parent)
        RichTextMixin.__init__(self)
