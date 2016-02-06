from jupyter_interface.chat_console_app import ChatConsoleApp
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
    #ChatConsoleApp.existing = 'tester'
    ChatConsoleApp.widget_factory = MainWidget
    ChatConsoleApp._plain_changed = _plain_changed
    ChatConsoleApp.launch_instance()

if __name__ == '__main__':
    main()

