from PyQt4 import QtGui

from qtconsole import qtconsoleapp
from qtconsole.jupyter_widget import JupyterWidget
from qtconsole.rich_jupyter_widget import RichJupyterWidget


def cloned_control(self):
    if self.kind == 'rich':
        control = QtGui.QTextEdit()
        control.setAcceptRichText(False)
        control.setMouseTracking(True)
    else:
        control = QtGui.QPlainTextEdit()
    return control


def cloned_page_control(self):
    if self.kind == 'rich':
        control = QtGui.QTextEdit()
    else:
        control = QtGui.QPlainTextEdit()
    return control

# assign custom_control and custom_page_control for the widgets

RichWidgetCreator = RichJupyterWidget
RichWidgetCreator.custom_control = cloned_control
RichWidgetCreator.custom_Page_control = cloned_page_control

# make plain controls?
PlainWidgetCreator = JupyterWidget
PlainWidgetCreator.custom_control = cloned_control
PlainWidgetCreator.custom_page_control = cloned_page_control


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
