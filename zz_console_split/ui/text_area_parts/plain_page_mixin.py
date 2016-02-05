from qtconsole.qt import QtCore, QtGui
from .base_event_filter import BaseEventFilter
from .context_menu import ContextMenu
__author__ = 'Manfred Minimair <manfred@minimair.org>'


class _ViewportFilter(BaseEventFilter):
    def __init__(self, text_area):
        super().__init__(text_area)

    def eventFilter(self, obj, event):
        intercepted = False
        event_type = event.type()
        # Make middle-click paste safe.
        if event_type == QtCore.QEvent.MouseButtonRelease and \
                event.button() == QtCore.Qt.MidButton and \
                obj == self.area.viewport():
            intercepted = True
            #cursor = self.area.cursorForPosition(event.pos())
            #self.area.setTextCursor(cursor)
            self.area.input_target.paste(QtGui.QClipboard.Selection)

        return intercepted

#         # Handle scrolling of the vsplit pager. This hack attempts to solve
#         # problems with tearing of the help text inside the pager window.  This
#         # happens only on Mac OS X with both PySide and PyQt. This fix isn't
#         # perfect but makes the pager more usable.
#         elif event_type in self._pager_scroll_events and \
#                 obj == self._page_control:
#            intercepted = True
#             self._page_control.repaint()


class PlainPageMixin(object):
    def __init__(self):
        pass

    def context_menu(self, pos, input_target, allow_paste=False):
        return ContextMenu(self, pos, input_target, allow_paste=False)

