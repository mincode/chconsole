import qtconsole.qtconsoleapp
from qtconsole.qtconsoleapp import JupyterQtConsoleApp

import main.expanded_main_window
from tab import RichTabMain, PlainTabMain

__author__ = 'Manfred Minimair <manfred@minimair.org>'

qtconsole.qtconsoleapp.MainWindow = main.expanded_main_window.ExpandedMainWindow


class ChatConsoleApp(JupyterQtConsoleApp):
    # widget_factory = RichTabMain
    widget_factory = PlainTabMain

    def init_qt_elements(self):
        super(ChatConsoleApp, self).init_qt_elements()
        self.window.setWindowTitle('Chat Console')
        self.window.active_frontend.main_content.entry.setFocus()

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
