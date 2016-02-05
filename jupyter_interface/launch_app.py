from jupyter_interface import qtconsoleapp
from jupyter_interface.main_widget import MainWidget

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def _plain_changed(self, name, old, new):
    kind = 'plain' if new else 'rich'
    self.config.ConsoleWidget.kind = kind
    if new:
        self.widget_factory = MainWidget
    else:
        self.widget_factory = MainWidget

#-----------------------------------------------------------------------------
# Main entry point
#-----------------------------------------------------------------------------

def main():
    #qtconsoleapp.JupyterQtConsoleApp.existing = 'tester'
    qtconsoleapp.JupyterQtConsoleApp.widget_factory = MainWidget
    qtconsoleapp.JupyterQtConsoleApp._plain_changed = _plain_changed
    qtconsoleapp.main()

if __name__ == '__main__':
    main()

