import sys, random
from PyQt4 import QtGui, QtCore


def new_tab_content(frontend):
    h_box = QtGui.QHBoxLayout()

    # command_view = QtGui.QFrame()
    command_view = QtGui.QTextEdit()
    command_view.setFrameShape(QtGui.QFrame.StyledPanel)
    command_view.setReadOnly(True)

    # command_entry = QtGui.QFrame()
    command_entry = QtGui.QTextEdit()
    command_entry.setFrameShape(QtGui.QFrame.StyledPanel)

    splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
    splitter.addWidget(command_view)
    splitter.addWidget(command_entry)

    trigger_filter = CommandTrigger(command_view, command_entry)
    command_entry.installEventFilter(trigger_filter)

    h_box.addWidget(splitter)
    frontend.setLayout(h_box)
    return splitter


def resize_splitter(splitter):
    sizes = splitter.sizes()
    # sizes_str = str(sizes)
    # command_view = splitter.widget(0)
    # command_view.insertPlainText(sizes_str+'\n')
    total_height = sum(sizes)
    num_widgets = len(sizes)
    height_first = (total_height * 3) // 4
    height_rest = total_height // 4
    new_sizes = [height_first]
    new_sizes.extend(height_rest for i in range(num_widgets - 1))
    splitter.setSizes(new_sizes)
    # sizes = splitter.sizes()
    # sizes_str = str(sizes)
    # command_view = splitter.widget(0)
    # command_view.insertPlainText(sizes_str+'\n')


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


class CommandTrigger(QtCore.QObject):
    def __init__(self, output, monitored):
        super().__init__(monitored)
        self.monitored = monitored
        self.output = output

    def eventFilter(self, obj, event):
        #self.output.insertPlainText('Event\n')
        if obj == self.monitored:
            #self.output.insertPlainText('Monitored Event\n')
            if event.type() == QtCore.QEvent.KeyPress:
                #self.output.insertPlainText('Monitored Key Event\n')
                ctrl_down = _control_key_down(event.modifiers())
                if ctrl_down:
                    #self.output.insertPlainText('Ctrl Down Event\n')
                    key = event.key()
                    #self.output.insertPlainText(str(key)+'\n')
                    if key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                        #self.output.insertPlainText('Ctrl-Enter\n')
                        #self.monitored.selectAll()
                        #self.monitored.cut()
                        doc = self.monitored.document()
                        doc_html = doc.toHtml()
                        self.output.insertHtml(doc_html)
                        self.output.insertPlainText('\n')
                        self.monitored.clear()
                        return True
        # standard event processing
        return QtCore.QObject.eventFilter(self, obj, event)


class MasterWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MasterWindow, self).__init__()
        self.tab_widget = QtGui.QTabWidget(self)
        self.init_tab()
        self.window_menu = self.menuBar().addMenu("&Window")
        self.init_menu_bar()
        self.init_ui()
        self.add_new_tab()

    def init_tab(self):
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested[int].connect(self.close_tab)

        self.setCentralWidget(self.tab_widget)
        # hide tab bar at first, since we have no tabs:
        self.tab_widget.tabBar().setVisible(False)
        # prevent focus in tab bar
        self.tab_widget.setFocusPolicy(QtCore.Qt.NoFocus)

    def init_ui(self):
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        #self.setGeometry(300, 300, 250, 150)
        self.setGeometry(300, 300, 500, 300)
        self.setWindowTitle('Icon')
        self.setWindowIcon(QtGui.QIcon('web.png'))
        self.show()

    def update_tab_bar_visibility(self):
        """ update visibility of the tabBar depending of the number of tab
        0 or 1 tab, tabBar hidden
        2+ tabs, tabBar visible
        send a self.close if number of tab ==0
        need to be called explicitly, or be connected to tabInserted/tabRemoved
        """
        if self.tab_widget.count() <= 1:
            self.tab_widget.tabBar().setVisible(False)
        else:
            self.tab_widget.tabBar().setVisible(True)
        if self.tab_widget.count() == 0:
            self.close()

    def close_tab(self,current_tab):
        """ Called when you need to try to close a tab.
        It takes the number of the tab to be closed as argument, or a reference
        to the widget inside this tab
        """

        # let's be sure "tab" and "closing widget" are respectively the index
        # of the tab to close and a reference to the frontend to close
        if type(current_tab) is not int :
            current_tab = self.tab_widget.indexOf(current_tab)
        closing_widget=self.tab_widget.widget(current_tab)


        # when trying to be closed, widget might re-send a request to be
        # closed again, but will be deleted when event will be processed. So
        # need to check that widget still exists and skip if not. One example
        # of this is when 'exit' is sent in a slave tab. 'exit' will be
        # re-sent by this function on the master widget, which ask all slave
        # widgets to exit
        if closing_widget is None:
            return
        self.tab_widget.removeTab(current_tab)
        self.update_tab_bar_visibility()

    # Populate the menu bar with common actions and shortcuts
    def add_menu_action(self, menu, action, defer_shortcut=False):
        """Add action to menu as well as self

        So that when the menu bar is invisible, its actions are still available.

        If defer_shortcut is True, set the shortcut context to widget-only,
        where it will avoid conflict with shortcuts already bound to the
        widgets themselves.
        """
        menu.addAction(action)
        self.addAction(action)

        if defer_shortcut:
            action.setShortcutContext(QtCore.Qt.WidgetShortcut)

    def make_frontend_visible(self,frontend):
        widget_index = self.tab_widget.indexOf(frontend)
        if widget_index > 0:
            self.tab_widget.setCurrentIndex(widget_index)

    def add_new_tab(self, name=None):
        """ insert a tab with a given frontend in the tab bar, and give it a name
        """
        if not name:
            name = 'Id %i' % (self.tab_widget.count()+random.randint(0,99))
        frontend = QtGui.QWidget()
        splitter = new_tab_content(frontend)
        self.tab_widget.addTab(frontend,name)
        self.update_tab_bar_visibility()
        self.make_frontend_visible(frontend)
        #frontend.exit_requested.connect(self.close_tab)
        resize_splitter(splitter)

    def init_tab_menu(self):
        self.tab_menu = self.menuBar().addMenu("&Tabs")
        # Qt on OSX maps Ctrl to Cmd, and Meta to Ctrl
        # keep the signal shortcuts to ctrl, rather than
        # platform-default like we do elsewhere.

        ctrl = "Meta" if sys.platform == 'darwin' else "Ctrl"

        self.new_tab_action = QtGui.QAction("&New tab",
                                            self,
                                            triggered=self.add_new_tab,
                                            shortcut=ctrl+"+T",
                                            )
        self.add_menu_action(self.tab_menu, self.new_tab_action)

    def next_tab(self):
        self.tab_widget.setCurrentIndex((self.tab_widget.currentIndex()+1))

    def prev_tab(self):
        self.tab_widget.setCurrentIndex((self.tab_widget.currentIndex()-1))

    def init_window_menu(self):
        if sys.platform == 'darwin':
            # add min/maximize actions to OSX, which lacks default bindings.
            self.minimizeAct = QtGui.QAction("Mini&mize",
                self,
                shortcut="Ctrl+m",
                statusTip="Minimize the window/Restore Normal Size",
                triggered=self.toggleMinimized)
            # maximize is called 'Zoom' on OSX for some reason
            self.maximizeAct = QtGui.QAction("&Zoom",
                self,
                shortcut="Ctrl+Shift+M",
                statusTip="Maximize the window/Restore Normal Size",
                triggered=self.toggleMaximized)

            self.add_menu_action(self.window_menu, self.minimizeAct)
            self.add_menu_action(self.window_menu, self.maximizeAct)
            self.window_menu.addSeparator()

        prev_key = "Ctrl+Shift+Left" if sys.platform == 'darwin' else "Ctrl+PgUp"
        self.prev_tab_act = QtGui.QAction("Pre&vious Tab",
            self,
            shortcut=prev_key,
            statusTip="Select previous tab",
            triggered=self.prev_tab)
        self.add_menu_action(self.window_menu, self.prev_tab_act)

        next_key = "Ctrl+Shift+Right" if sys.platform == 'darwin' else "Ctrl+PgDown"
        self.next_tab_act = QtGui.QAction("Ne&xt Tab",
            self,
            shortcut=next_key,
            statusTip="Select next tab",
            triggered=self.next_tab)
        self.add_menu_action(self.window_menu, self.next_tab_act)

    def init_menu_bar(self):
        #create menu in the order they should appear in the menu bar
        self.init_tab_menu()
        self.init_window_menu()


class MasterApp(QtGui.QApplication):
    window = None

    def __init__(self, argv):
        super(MasterApp, self).__init__(argv)

    def run(self):
        window = MasterWindow()
        sys.exit(self.exec_())


def main():

    app = MasterApp(sys.argv)
    app.run()


if __name__ == '__main__':
    main()
