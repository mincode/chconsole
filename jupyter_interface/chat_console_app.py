import qtconsole.qtconsoleapp
import jupyter_interface.expanded_main_window
from qtconsole.qtconsoleapp import JupyterQtConsoleApp
from jupyter_interface.tab_main import RichTabMain, PlainTabMain

__author__ = 'Manfred Minimair <manfred@minimair.org>'

qtconsole.qtconsoleapp.MainWindow = jupyter_interface.expanded_main_window.ExpandedMainWindow


class ChatConsoleApp(JupyterQtConsoleApp):
    widget_factory = RichTabMain

    def init_qt_elements(self):
        super(ChatConsoleApp, self).init_qt_elements()
        self.window.setWindowTitle('Chat Console')

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
            self.widget_factory = PlainTabMain
        else:  # rich
            self.widget_factory = RichTabMain
