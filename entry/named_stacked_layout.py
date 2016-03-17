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
        return self.insertWidget(index, w)

    def set_current_widget(self, name):
        """
        Set current widget by name.
        :param name: name of the widget.
        :return:
        """
        self.setCurrentWidget(self.by_name[name])

    @property
    def current_widget(self):
        """
        Current widget on top of the stack.
        :return: the current widget.
        """
        return self.current_widget()

    def clear(self):
        """
        Clear all widgets in stack.
        :return:
        """
        for name in self.by_name:
            self.by_name[name].clear()
