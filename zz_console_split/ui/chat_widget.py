__author__ = 'Manfred Minimair <manfred@minimair.org>'

#        self.customContextMenuRequested.connect(self._custom_context_menu_requested)

def _custom_context_menu_requested(self, pos):
    """ Shows a context menu at the given QPoint (in widget coordinates).
    """
# need to determine which subwidget viewport contains pos
    menu = self.make_context_menu(pos)
    menu.exec_(self.mapToGlobal(pos))

"""
class _ViewportFilter(BaseEventFilter):
    def __init__(self, text_area):
        super().__init__(text_area)

    def eventFilter(self, obj, event):
        intercepted = False
        event_type = event.type()
        # Make middle-click paste safe.
# depends on obj where to paste
        if event_type == QtCore.QEvent.MouseButtonRelease and \
                event.button() == QtCore.Qt.MidButton and \
                obj == self.area.viewport():
            intercepted = True
            cursor = self.area.input_target.cursorForPosition(event.pos())
            self.area.input_target.setTextCursor(cursor)
            self.area.input_target.paste(QtGui.QClipboard.Selection)

        return intercepted
"""