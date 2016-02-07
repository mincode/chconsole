import sys
from qtconsole.qt import QtGui
from qtconsole import mainwindow

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class ExpandedMainWindow(mainwindow.MainWindow):
    """
    Expansion of qtconsole.mainwindow.MainWindow
    """
    def __init__(self,
                 app,
                 confirm_exit=True,
                 new_frontend_factory=None, slave_frontend_factory=None):
        super(ExpandedMainWindow, self).__init__(app, confirm_exit, new_frontend_factory, slave_frontend_factory)
        self.pager_menu = None

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
