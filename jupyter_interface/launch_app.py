import qtconsole.qtconsoleapp
import jupyter_interface.expanded_main_window
from jupyter_interface.chat_console_app import ChatConsoleApp
from jupyter_interface.tab_widget import RichTabWidget, PlainTabWidget

qtconsole.qtconsoleapp.MainWindow = jupyter_interface.expanded_main_window.ExpandedMainWindow

__author__ = 'Manfred Minimair <manfred@minimair.org>'


# traitlets handler
def _plain_changed(self, name, old, new):
    """
    Change type of text edit used.
    :param self: ChatConsoleApp
    :param name: dummy
    :param old: dummy
    :param new: True if new type of text edit is plain, and false if it is rich.
    :return:
    """

    if new:  # plain
        self.widget_factory = PlainTabWidget
    else:  # rich
        self.widget_factory = RichTabWidget

#-----------------------------------------------------------------------------
# Main entry point
#-----------------------------------------------------------------------------

def main():
    #Use if existing kernel: kernel-tester.json
    #ChatConsoleApp.existing = 'tester'
    ChatConsoleApp.widget_factory = RichTabWidget
    ChatConsoleApp._plain_changed = _plain_changed
    ChatConsoleApp.launch_instance()

if __name__ == '__main__':
    main()

