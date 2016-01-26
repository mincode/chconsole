from qtconsole import qtconsoleapp
from qtconsole.jupyter_widget import JupyterWidget
from qtconsole.rich_jupyter_widget import RichJupyterWidget

#qtconsoleapp.main()
#qtconsoleapp.JupyterQtConsoleApp.existing = 'tester'

# assign custom_control and custom_page_control for the widgets
#qtconsoleapp.JupyterQtConsoleApp.widget_factory = JupyterWidget
qtconsoleapp.JupyterQtConsoleApp.widget_factory = RichJupyterWidget

#redefine
#   def _plain_changed(self, name, old, new):
#        kind = 'plain' if new else 'rich'
#        self.config.ConsoleWidget.kind = kind
#        if new:
#            self.widget_factory = JupyterWidget
#        else:
#            self.widget_factory = RichJupyterWidget

qtconsoleapp.JupyterQtConsoleApp.launch_instance()
