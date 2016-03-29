from qtconsole.qt import QtGui

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class NamedStackedLayout(QtGui.QStackedLayout):
    by_name = None  # dict: name -> widget in the stack

    def __init__(self, parent=None):
        super(NamedStackedLayout, self).__init__(parent)
        self.by_name = dict()

    def insert_widget(self, index, w, name):
        """
        Insert widget into stacked layout.
        :param index: index of the widget w in the stack; if out of range, then widget is appended.
        :param w: widget.
        :param name: name of the widget.
        :return: actual index of the inserted widget.
        """
        self.by_name[name] = w
        setattr(w, 'name', name)
        return self.insertWidget(index, w)

    def set_current_widget(self, name):
        """
        Set current widget by name.
        :param name: name of the widget.
        :return:
        """
        self.setCurrentWidget(self.by_name[name])

    def move(self):
        """
        Make next widget in the stack the current widget.
        :return:
        """
        index = self.currentIndex() + 1
        if self.widget(index) is None:
            index = 0
        self.setCurrentIndex(index)

    def apply(self, command, *args, **kwargs):
        """
        Apply command to all members of the stack.
        :param command: name of the command.
        :param args: arguments for the command.
        :param kwargs: keyword arguments for the command.
        :return:
        """
        for name in self.by_name:
            getattr(self.by_name[name], command, None)(*args, **kwargs)

    def clear(self):
        """
        Clear all widgets in stack.
        :return:
        """
        self.apply('clear')

    def set_read_only(self, state=False):
        self.apply('setReadOnly', state)