#failed
#too many constraints on the control by qtconsole
#will try to redo MainWindow to include a command_view per tab


from qtconsole.qt import QtGui, QtCore

from traitlets.config.configurable import LoggingConfigurable
from qtconsole.util import MetaQObjectHasTraits


class SplitControl(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, QtGui.QWidget), {})):
    command_view = None
    command_entry = None
    splitter = None

    def __init__(self, parent=None, **kwargs):
        QtGui.QWidget.__init__(self, parent)
        LoggingConfigurable.__init__(self, **kwargs)

        self.command_view = QtGui.QTextEdit()
        self.command_view.setFrameShape(QtGui.QFrame.StyledPanel)
        self.command_view.setReadOnly(True)

        self.command_entry = QtGui.QTextEdit()
        self.command_entry.setFrameShape(QtGui.QFrame.StyledPanel)
        self.command_entry.setAcceptRichText(False)

        #trigger_filter = CommandTrigger(command_view, command_entry)
        #command_entry.installEventFilter(trigger_filter)

        self.splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.command_view)
        self.splitter.addWidget(self.command_entry)

        horizontal_box = QtGui.QHBoxLayout()
        horizontal_box.addWidget(self.splitter)

        self.setLayout(horizontal_box)
        self.setMouseTracking(True)

    def viewport(self):
        return self.command_entry.viewport()
