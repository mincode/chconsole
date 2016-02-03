import qtconsole.qt

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class ContextMenu(qtconsole.qt.QtGui.QMenu):
    def __init__(self, parent, pos, input_target, allow_paste=True):
        """ Creates a context menu for the given QPoint (in widget coordinates).
        """
        super(ContextMenu, self).__init__(parent)

        if parent == input_target:
            parent.cut_action = self.addAction('Cut', parent.cut)
            parent.cut_action.setEnabled(parent.can_cut())
            parent.cut_action.setShortcut(qtconsole.qt.QtGui.QKeySequence.Cut)

        parent.copy_action = self.addAction('Copy', parent.copy)
        parent.copy_action.setEnabled(parent.can_copy())
        parent.copy_action.setShortcut(qtconsole.qt.QtGui.QKeySequence.Copy)

        if allow_paste:
            parent.paste_action = self.addAction('Paste', input_target.paste)
            parent.paste_action.setEnabled(input_target.can_paste())
            parent.paste_action.setShortcut(qtconsole.qt.QtGui.QKeySequence.Paste)

        anchor = parent.anchorAt(pos)
        if anchor:
            self.addSeparator()
            parent.copy_link_action = self.addAction(
                'Copy Link Address', lambda: parent.copy_anchor(anchor=anchor))
            parent.open_link_action = self.addAction(
                'Open Link', lambda: parent.open_anchor(anchor=anchor))

        self.addSeparator()
        self.addAction(parent.select_all_action)

        self.addSeparator()
        self.addAction(parent.export_action)
        self.addAction(parent.print_action)


class OutMenu(ContextMenu):
    def __init__(self, parent, pos, input_target):
        super(OutMenu,self).__init__(parent, pos, input_target, allow_paste=True)


class PagePasteMenu(ContextMenu):
    def __init__(self, parent, pos, input_target):
        super(PagePasteMenu, self).__init__(parent, pos, input_target, allow_paste=True)


class PageNoPasteMenu(ContextMenu):
    def __init__(self, parent, pos, input_target):
        super(PageNoPasteMenu, self).__init__(parent, pos, input_target, allow_paste=False)


class InMenu(ContextMenu):
    def __init__(self, parent, pos):
        super(InMenu,self).__init__(parent, pos, parent, allow_paste=True)
