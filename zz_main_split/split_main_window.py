from qtconsole.qt import QtCore, QtGui
from functools import singledispatch
from qtconsole import mainwindow

from zz_main_split.signal_content import SignalContent, HtmlSignal, TextSignal


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


@singledispatch
def insert_signal_content(output, target):
    raise NotImplementedError


@insert_signal_content.register(TextSignal)
def _(output, target):
    target.insertPlainText(output.content)


@insert_signal_content.register(HtmlSignal)
def _(output, target):
    target.insertHtml(output.content)


class SplitWidget(QtGui.QWidget):
    command_view = None
    command_entry = None
    splitter = None

    #confirm_restart = Bool(True, config=True,
    #    help="Whether to ask for user confirmation when restarting kernel")

    def __init__(self, front_end, parent=None):
        super(SplitWidget, self).__init__(parent)
        self.command_view = QtGui.QTextEdit()
        self.command_view.setFrameShape(QtGui.QFrame.StyledPanel)
        self.command_view.setReadOnly(True)

        self.command_entry = front_end
        #Needed to start the widget:
        self.confirm_restart = front_end.confirm_restart
        #Needed to safely close the widget:
        self.kernel_client = front_end.kernel_client
        self.kernel_manager = front_end.kernel_manager
        self._existing = front_end._existing

        #Connect output slot
        self.command_entry.signaller.connect_signal(self.insert_command_view)

        #trigger_filter = CommandTrigger(command_view, command_entry)
        #command_entry.installEventFilter(trigger_filter)

        self.splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.command_view)
        self.splitter.addWidget(self.command_entry)

        horizontal_box = QtGui.QHBoxLayout()
        horizontal_box.addWidget(self.splitter)

        self.setLayout(horizontal_box)

    @QtCore.Slot(SignalContent)
    def insert_command_view(self, output):
        #self.command_view.insertPlainText(output.content)
        insert_signal_content(output, self.command_view)


class MainWindow(mainwindow.MainWindow):
    def __init__(self,
                 app,
                 confirm_exit=True,
                 new_frontend_factory=None, slave_frontend_factory=None):
        super().__init__(app, confirm_exit, new_frontend_factory, slave_frontend_factory)
        # print('split_main_window')

    def add_tab_with_frontend(self, frontend, name=None):
        """ insert a tab with a given frontend in the tab bar, and give it a name

        """
        if not name:
            name = 'kernel %i' % self.next_kernel_id

        split_frontend = SplitWidget(frontend)
        self.tab_widget.addTab(split_frontend, name)
        self.update_tab_bar_visibility()
        self.make_frontend_visible(frontend)
        frontend.exit_requested.connect(self.close_tab)
