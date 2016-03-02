import sys
from qtconsole.qt import QtGui, QtCore
from qtconsole import mainwindow
from ui.statusbar import StatusBar
from ui.entry import code_active_color, chat_active_color

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class ExpandedMainWindow(mainwindow.MainWindow):
    """
    Expansion of qtconsole.mainwindow.MainWindow
    """
    status_bar = None
    _entry_update_code = None  # handler connected with main_content to update the code flag of the entry field
    _act_on_send = None  # handler connected with main_content to act on send clicked
    _act_on_frontend = None  # handler connected with main_content to act on message to frontend

    def __init__(self,
                 app,
                 confirm_exit=True,
                 new_frontend_factory=None, slave_frontend_factory=None):
        super(ExpandedMainWindow, self).__init__(app, confirm_exit, new_frontend_factory, slave_frontend_factory)
        self.pager_menu = None
        self.status_bar = StatusBar(code_checked_color=code_active_color, chat_checked_color=chat_active_color)
        self.setStatusBar(self.status_bar)
        self.tab_widget.currentChanged.connect(self.connect_code_activity)

    def connect_code_activity(self):
        if self.active_frontend is None:
            return
        active = self.active_frontend
        if self._entry_update_code:
            self.status_bar.code_toggled.disconnect(self._entry_update_code)
        self._entry_update_code = active.main_content.entry.update_code_mode

        self.status_bar.code_toggled.connect(self._entry_update_code)
        self.status_bar.update_code(active.main_content.entry.code_mode)

        if self._act_on_send:
            self.status_bar.send_clicked.disconnect(self._act_on_send)
        self._act_on_send = active.main_content.on_send_clicked
        self.status_bar.send_clicked.connect(self._act_on_send)

        if self._act_on_frontend:
            self.status_bar.send_clicked.disconnect(self._act_on_frontend)
        self._act_on_frontend = active.main_content.on_frontend_clicked
        self.status_bar.frontend_clicked.connect(self._act_on_frontend)

    def set_paging_active_frontend(self, paging):
        """
        Adjust the pager location paging of the active frontend.
        :param paging: String.
        :return: A function of type ()->None that sets the paging location.
        """
        def set_paging():
            self.active_frontend.main_content.pager.location = paging
        return set_paging

    def init_view_menu(self):
        """
        Initialize the view menu.
        :return:
        """
        self.view_menu = self.menuBar().addMenu("&View")

        if sys.platform != 'darwin':
            # disable on OSX, where there is always a menu bar
            self.toggle_menu_bar_act = QtGui.QAction("Toggle &Menu Bar",
                self,
                shortcut="Ctrl+Shift+M",
                statusTip="Toggle visibility of menubar",
                triggered=self.toggle_menu_bar)
            self.add_menu_action(self.view_menu, self.toggle_menu_bar_act)

        fs_key = "Ctrl+Meta+F" if sys.platform == 'darwin' else "F11"
        self.full_screen_act = QtGui.QAction("&Full Screen",
            self,
            shortcut=fs_key,
            statusTip="Toggle between Fullscreen and Normal Size",
            triggered=self.toggleFullScreen)
        self.add_menu_action(self.view_menu, self.full_screen_act)

        self.view_menu.addSeparator()

        self.increase_font_size = QtGui.QAction("Zoom &In",
            self,
            shortcut=QtGui.QKeySequence.ZoomIn,
            triggered=self.increase_font_size_active_frontend
            )
        self.add_menu_action(self.view_menu, self.increase_font_size, True)

        self.decrease_font_size = QtGui.QAction("Zoom &Out",
            self,
            shortcut=QtGui.QKeySequence.ZoomOut,
            triggered=self.decrease_font_size_active_frontend
            )
        self.add_menu_action(self.view_menu, self.decrease_font_size, True)

        self.reset_font_size = QtGui.QAction("Zoom &Reset",
            self,
            shortcut="Ctrl+0",
            triggered=self.reset_font_size_active_frontend
            )
        self.add_menu_action(self.view_menu, self.reset_font_size, True)

        self.view_menu.addSeparator()

        self.clear_action = QtGui.QAction("&Clear Screen",
            self,
            shortcut='Ctrl+L',
            statusTip="Clear the console",
            triggered=self.clear_active_frontend)
        self.add_menu_action(self.view_menu, self.clear_action)

        pager_locations = self.active_frontend.main_content.pager_locations
        if len(pager_locations)>1:
            self.pager_menu = self.view_menu.addMenu("&Pager")
            for location in pager_locations:
                pager_action = QtGui.QAction('&'+location.capitalize(), self,
                    triggered=self.set_paging_active_frontend(location))
                self.pager_menu.addAction(pager_action)

    # MM: This method does not seem to be in use.
    def _set_active_frontend_focus(self):
        QtCore.QTimer.singleShot(200, self.active_frontend.main_content.entry.setFocus)

    # The following depend on where the focus is in the active frontend.
    def print_action_active_frontend(self):
        self.active_frontend.main_content.print_action.trigger()

    def export_action_active_frontend(self):
        self.active_frontend.main_content.export_action.trigger()

    def select_all_active_frontend(self):
        self.active_frontend.main_content.select_all_action.trigger()

    def increase_font_size_active_frontend(self):
        self.active_frontend.main_content.increase_font_size.trigger()

    def decrease_font_size_active_frontend(self):
        self.active_frontend.main_content.decrease_font_size.trigger()

    def reset_font_size_active_frontend(self):
        self.active_frontend.main_content.reset_font_size.trigger()

    def clear_active_frontend(self):
        self.active_frontend.main_content.clear()

    def cut_active_frontend(self):
        widget = self.active_frontend
        if widget.main_content.can_cut():
            widget.main_content.cut()

    def copy_active_frontend(self):
        widget = self.active_frontend
        widget.main_content.copy()

    def copy_raw_active_frontend(self):
        self.active_frontend.main_content.copy_raw_action.trigger()

    def paste_active_frontend(self):
        widget = self.active_frontend
        if widget.main_content.can_paste():
            widget.main_content.paste()

    def undo_active_frontend(self):
        self.active_frontend.main_content.undo()

    def redo_active_frontend(self):
        self.active_frontend.main_content.redo()

    def print_action_active_frontend(self):
        self.active_frontend.main_content.print_action.trigger()

    def export_action_active_frontend(self):
        self.active_frontend.main_content.export_action.trigger()

    def select_all_active_frontend(self):
        self.active_frontend.main_content.select_all_action.trigger()

    def increase_font_size_active_frontend(self):
        self.active_frontend.main_content.increase_font_size.trigger()

    def decrease_font_size_active_frontend(self):
        self.active_frontend.main_content.decrease_font_size.trigger()

    def reset_font_size_active_frontend(self):
        self.active_frontend.main_content.reset_font_size.trigger()
