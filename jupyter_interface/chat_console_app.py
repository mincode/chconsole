from qtconsole.qtconsoleapp import JupyterQtConsoleApp

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class ChatConsoleApp(JupyterQtConsoleApp):
    def init_qt_elements(self):
        super(ChatConsoleApp, self).init_qt_elements()
        self.window.setWindowTitle('Chat Console')
