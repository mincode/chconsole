import sys

import qtconsole.mainwindow
from qtconsole import mainwindow
from qtconsole.qt import QtGui, QtCore
from chconsole.standards import code_active_color, chat_active_color
from .statusbar import StatusBar

background = qtconsole.mainwindow.background

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class ExpandedMainWindow(mainwindow.MainWindow):
    """
    Expansion of qtconsole.mainwindow.MainWindow
    """
    status_bar = None
    _entry_update_current = None  # handler connected with main_content to update the code flag of the entry field
    _act_on_enter = None  # handler connected with main_content to act on send clicked
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
        if self._entry_update_current:
            self.status_bar.activated.disconnect(self._entry_update_current)
        self._entry_update_current = active.main_content.entry.switch

        self.status_bar.activated.connect(self._entry_update_current)
        self.status_bar.update_current(active.main_content.entry.current_widget.name)

        active.main_content.entry.new_current.connect(self.status_bar.update_current)

        if self._act_on_enter:
            self.status_bar.enter_clicked.disconnect(self._act_on_enter)
        self._act_on_enter = active.main_content.on_enter_clicked
        self.status_bar.enter_clicked.connect(self._act_on_enter)

        if self._act_on_frontend:
            self.status_bar.frontend_clicked.disconnect(self._act_on_frontend)
        self._act_on_frontend = active.main_content.on_frontend_clicked
        self.status_bar.frontend_clicked.connect(self._act_on_frontend)

        self.status_bar.kernel_clicked.connect(self._on_kernel_clicked)

    # For debugging
    def _on_kernel_clicked(self):
        active = self.active_frontend
        active.is_complete('def f():\n\treturn 0\n\n')
        active.is_complete('x=1')

    def set_paging_active_frontend(self, paging):
        """
        Adjust the pager location paging of the active frontend.
        :param paging: String.
        :return: A function of type ()->None that sets the paging location.
        """
        def set_paging():
            self.active_frontend.main_content.pager.location = paging
        return set_paging

    def init_edit_menu(self):
        self.edit_menu = self.menuBar().addMenu("&Edit")

        self.undo_action = QtGui.QAction("&Undo",
            self,
            shortcut=QtGui.QKeySequence.Undo,
            statusTip="Undo last action if possible",
            triggered=self.undo_active_frontend
            )
        self.add_menu_action(self.edit_menu, self.undo_action)

        self.redo_action = QtGui.QAction("&Redo",
            self,
            shortcut=QtGui.QKeySequence.Redo,
            statusTip="Redo last action if possible",
            triggered=self.redo_active_frontend)
        self.add_menu_action(self.edit_menu, self.redo_action)

        self.edit_menu.addSeparator()

        self.cut_action = QtGui.QAction("&Cut",
            self,
            shortcut=QtGui.QKeySequence.Cut,
            triggered=self.cut_active_frontend
            )
        self.add_menu_action(self.edit_menu, self.cut_action, True)

        self.copy_action = QtGui.QAction("&Copy",
            self,
            shortcut=QtGui.QKeySequence.Copy,
            triggered=self.copy_active_frontend
            )
        self.add_menu_action(self.edit_menu, self.copy_action, True)

        self.paste_action = QtGui.QAction("&Paste",
            self,
            shortcut=QtGui.QKeySequence.Paste,
            triggered=self.paste_active_frontend
            )
        self.add_menu_action(self.edit_menu, self.paste_action, True)

        self.edit_menu.addSeparator()

        selectall = QtGui.QKeySequence(QtGui.QKeySequence.SelectAll)
        if selectall.matches("Ctrl+A") and sys.platform != 'darwin':
            # Only override the default if there is a collision.
            # Qt ctrl = cmd on OSX, so the match gets a false positive on OSX.
            selectall = "Ctrl+Shift+A"
        self.select_all_action = QtGui.QAction("Select &All",
            self,
            shortcut=selectall,
            triggered=self.select_all_active_frontend
            )
        self.add_menu_action(self.edit_menu, self.select_all_action, True)

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

        self.view_menu.addSeparator()

        self.show_users_action = QtGui.QAction("&Show User Names",
            self,
            checkable=True,
#            checked=self.active_frontend.main_content.show_users,
            triggered=self.toggle_confirm_show_users)
        self.show_users_action.setChecked(self.active_frontend.main_content.show_users)
        self.add_menu_action(self.view_menu, self.show_users_action)
        self.tab_widget.currentChanged.connect(self.update_show_users_checkbox)

    def toggle_confirm_show_users(self):
        widget = self.active_frontend
        widget.main_content.show_users = not widget.main_content.show_users
        self.show_users_action.setChecked(widget.main_content.show_users)

    def update_show_users_checkbox(self):
        if self.active_frontend is None:
            return
        widget = self.active_frontend
        self.show_users_action.setChecked(widget.main_content.show_users)


    # MM: This method does not seem to be in use.
    def _set_active_frontend_focus(self):
        QtCore.QTimer.singleShot(200, self.active_frontend.main_content.entry.set_focus)

    # The following depend on where the focus is in the active frontend.
    def print_action_active_frontend(self):
        self.active_frontend.main_content.call_focus_method('print_action.trigger')

    def export_action_active_frontend(self):
        self.active_frontend.main_content.call_focus_method('export_action.trigger')

    def select_all_active_frontend(self):
        self.active_frontend.main_content.call_focus_method('select_all_action.trigger')

    def increase_font_size_active_frontend(self):
        self.active_frontend.main_content.call_focus_method('increase_font_size.trigger')

    def decrease_font_size_active_frontend(self):
        self.active_frontend.main_content.call_focus_method('decrease_font_size.trigger')

    def reset_font_size_active_frontend(self):
        self.active_frontend.main_content.call_focus_method('reset_font_size.trigger')

    def clear_active_frontend(self):
        self.active_frontend.main_content.call_focus_method('clear')

    def cut_active_frontend(self):
        widget = self.active_frontend
        if widget.main_content.call_focus_method('can_cut'):
            widget.main_content.call_focus_method('cut')

    def copy_active_frontend(self):
        widget = self.active_frontend
        widget.main_content.call_focus_method('copy')

    def paste_active_frontend(self):
        widget = self.active_frontend
        if widget.main_content.call_focus_method('can_paste'):
            widget.main_content.call_focus_method('paste')

    def undo_active_frontend(self):
        self.active_frontend.main_content.call_focus_method('undo')

    def redo_active_frontend(self):
        self.active_frontend.main_content.call_focus_method('redo')

    def close_tab(self, current_tab):
        """ Called when you need to try to close a tab.

        It takes the number of the tab to be closed as argument, or a reference
        to the widget inside this tab
        """

        # let's be sure "tab" and "closing widget" are respectively the index
        # of the tab to close and a reference to the frontend to close
        if type(current_tab) is not int:
            current_tab = self.tab_widget.indexOf(current_tab)
        closing_widget = self.tab_widget.widget(current_tab)

        # when trying to be closed, widget might re-send a request to be
        # closed again, but will be deleted when event will be processed. So
        # need to check that widget still exists and skip if not. One example
        # of this is when 'exit' is sent in a slave tab. 'exit' will be
        # re-sent by this function on the master widget, which ask all slave
        # widgets to exit
        if closing_widget is None:
            return

        # get a list of all slave widgets on the same kernel.
        slave_tabs = self.find_slave_widgets(closing_widget)

        keepkernel = None  # Use the prompt by default
        if hasattr(closing_widget, '_keep_kernel_on_exit'):  # set by exit magic
            keepkernel = closing_widget._keep_kernel_on_exit
            # If signal sent by exit magic (_keep_kernel_on_exit, exist and not None)
            # we set local slave tabs._hidden to True to avoid prompting for kernel
            # restart when they get the signal. and then "forward" the 'exit'
            # to the main window
            if keepkernel is not None:
                for tab in slave_tabs:
                    tab._hidden = True
                if closing_widget in slave_tabs:
                    try:
                        self.find_master_tab(closing_widget).execute('exit')
                    except AttributeError:
                        self.log.info("Master already closed or not local, closing only current tab")
                        self.tab_widget.removeTab(current_tab)
                    self.update_tab_bar_visibility()
                    return

        kernel_client = closing_widget.kernel_client
        kernel_manager = closing_widget.kernel_manager

        if keepkernel is None and not closing_widget._confirm_exit:
            # don't prompt, just terminate the kernel if we own it
            # or leave it alone if we don't
            keepkernel = closing_widget._existing
        if keepkernel is None:  # show prompt
            if kernel_client and kernel_client.channels_running:
                title = self.window().windowTitle()
                cancel = QtGui.QMessageBox.Cancel
                okay = QtGui.QMessageBox.Ok
                if closing_widget._may_close:
                    msg = "You are closing the tab : " + '"' + self.tab_widget.tabText(current_tab) + '"'
                    info = "Would you like to quit the Kernel and close all attached Consoles as well?"
                    justthis = QtGui.QPushButton("&No, just this Tab", self)
                    justthis.setShortcut('N')
                    closeall = QtGui.QPushButton("&Yes, close all", self)
                    closeall.setShortcut('Y')
                    # allow ctrl-d ctrl-d exit, like in terminal
                    closeall.setShortcut('Ctrl+D')
                    box = QtGui.QMessageBox(QtGui.QMessageBox.Question,
                                            title, msg)
                    box.setInformativeText(info)
                    box.addButton(cancel)
                    box.addButton(justthis, QtGui.QMessageBox.NoRole)
                    box.addButton(closeall, QtGui.QMessageBox.YesRole)
                    box.setDefaultButton(closeall)
                    box.setEscapeButton(cancel)
                    pixmap = QtGui.QPixmap(self._app.icon.pixmap(QtCore.QSize(64, 64)))
                    box.setIconPixmap(pixmap)
                    reply = box.exec_()
                    if reply == 1:  # close All
                        for slave in slave_tabs:
                            background(slave.kernel_client.stop_channels)
                            self.tab_widget.removeTab(self.tab_widget.indexOf(slave))
                        kernel_manager.shutdown_kernel()
                        self.tab_widget.removeTab(current_tab)
                        background(kernel_client.stop_channels)
                    elif reply == 0:  # close Console
                        if not closing_widget._existing:
                            # Have kernel: don't quit, just close the tab
                            closing_widget.execute("exit True")
                        self.tab_widget.removeTab(current_tab)
                        background(kernel_client.stop_channels)
                else:
                    reply = QtGui.QMessageBox.question(self, title,
                                                       "Are you sure you want to close this Console?",
                                                       okay | cancel,
                                                       defaultButton=okay
                                                       )
                    if reply == okay:
                        self.tab_widget.removeTab(current_tab)
        elif keepkernel:  # close console but leave kernel running (no prompt)
            self.tab_widget.removeTab(current_tab)
            background(kernel_client.stop_channels)
        else:  # close console and kernel (no prompt)
            self.tab_widget.removeTab(current_tab)
            if kernel_client and kernel_client.channels_running:
                for slave in slave_tabs:
                    background(slave.kernel_client.stop_channels)
                    self.tab_widget.removeTab(self.tab_widget.indexOf(slave))
                if kernel_manager:
                    kernel_manager.shutdown_kernel()
                background(kernel_client.stop_channels)

        self.update_tab_bar_visibility()

