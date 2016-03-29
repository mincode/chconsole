from qtconsole.qt import QtGui

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class TextContextMenu(QtGui.QMenu):
    def __init__(self, parent, pos):
        """ Creates a context menu for the given QPoint (in widget coordinates).
        """
        super(TextContextMenu, self).__init__(parent)

        if not parent.isReadOnly():
            parent.cut_action = self.addAction('Cut', parent.cut)
            parent.cut_action.setEnabled(parent.can_cut())
            parent.cut_action.setShortcut(QtGui.QKeySequence.Cut)

        parent.copy_action = self.addAction('Copy', parent.copy)
        parent.copy_action.setEnabled(parent.can_copy())
        parent.copy_action.setShortcut(QtGui.QKeySequence.Copy)

        if not parent.isReadOnly():
            parent.paste_action = self.addAction('Paste', parent.paste)
            parent.paste_action.setEnabled(parent.can_paste())
            parent.paste_action.setShortcut(QtGui.QKeySequence.Paste)

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
