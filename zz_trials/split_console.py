#failed
#too many constraints on the control by qtconsole
#will try to redo MainWindow to include a command_view per tab


from PyQt4 import QtGui, QtCore

from qtconsole import qtconsoleapp
from qtconsole.jupyter_widget import JupyterWidget
from qtconsole.rich_jupyter_widget import RichJupyterWidget


class SplitControl(QtGui.QWidget):
    command_view = None
    command_entry = None
    splitter = None

    def __init__(self, *args):
        super(SplitControl, self).__init__(*args)
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


# def _create_control(self):
#     """ Creates and connects the underlying text widget.
#     """
#     # Create the underlying control.
#     if self.custom_control:
#         control = self.custom_control()
#     elif self.kind == 'plain':
#         control = QtGui.QPlainTextEdit()
#     elif self.kind == 'rich':
#         control = QtGui.QTextEdit()
#         control.setAcceptRichText(False)
#         control.setMouseTracking(True)
#
#     # Prevent the widget from handling drops, as we already provide
#     # the logic in this class.
#     control.setAcceptDrops(False)
#
#     # Install event filters. The filter on the viewport is needed for
#     # mouse events.
#     control.installEventFilter(self)
#     control.viewport().installEventFilter(self)
#
#     # Connect signals.
#     control.customContextMenuRequested.connect(
#         self._custom_context_menu_requested)
#     control.copyAvailable.connect(self.copy_available)
#     control.redoAvailable.connect(self.redo_available)
#     control.undoAvailable.connect(self.undo_available)
#
#     # Hijack the document size change signal to prevent Qt from adjusting
#     # the viewport's scrollbar. We are relying on an implementation detail
#     # of Q(Plain)TextEdit here, which is potentially dangerous, but without
#     # this functionality we cannot create a nice terminal interface.
#     layout = control.document().documentLayout()
#     layout.documentSizeChanged.disconnect()
#     layout.documentSizeChanged.connect(self._adjust_scrollbars)
#
#     # Configure the control.
#     control.setAttribute(QtCore.Qt.WA_InputMethodEnabled, True)
#     control.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
#     control.setReadOnly(True)
#     control.setUndoRedoEnabled(False)
#     control.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
#     return control

def _create_control(self):
    """ Creates and connects the underlying text widget.
    """
    # Create the underlying control.
    if self.custom_control:
        control = self.custom_control()
    elif self.kind == 'plain':
        control = QtGui.QPlainTextEdit()
    elif self.kind == 'rich':
        control = QtGui.QTextEdit()
        control.setAcceptRichText(False)
        control.setMouseTracking(True)

    # Prevent the widget from handling drops, as we already provide
    # the logic in this class.
    control.setAcceptDrops(False)

    # Install event filters. The filter on the viewport is needed for
    # mouse events.
    control.installEventFilter(self)
    control.viewport().installEventFilter(self)

    return control


def split_control(self):
    if self.kind == 'rich':
        control = SplitControl()
    else:
        control = QtGui.QPlainTextEdit()
    return control


def split_page_control(self):
    if self.kind == 'rich':
        control = QtGui.QTextEdit()
    else:
        control = QtGui.QPlainTextEdit()
    return control

# assign custom_control and custom_page_control for the widgets

RichWidgetCreator = RichJupyterWidget
RichWidgetCreator.custom_control = split_control
RichWidgetCreator.custom_page_control = split_page_control
RichWidgetCreator._create_control = _create_control

# make plain controls?
PlainWidgetCreator = JupyterWidget
PlainWidgetCreator.custom_control = split_control
PlainWidgetCreator.custom_page_control = split_page_control
PlainWidgetCreator._create_control = _create_control


def _plain_changed(self, name, old, new):
    kind = 'plain' if new else 'rich'
    self.config.ConsoleWidget.kind = kind
    if new:
        self.widget_factory = PlainWidgetCreator
    else:
        self.widget_factory = RichWidgetCreator


qtconsoleapp.JupyterQtConsoleApp.widget_factory = RichWidgetCreator
qtconsoleapp.JupyterQtConsoleApp._plain_changed = _plain_changed
# Test Rich
#from IPython.display import Image
#Image(filename='squirrel.png')

#qtconsoleapp.JupyterQtConsoleApp.existing = 'tester'
qtconsoleapp.JupyterQtConsoleApp.launch_instance()
