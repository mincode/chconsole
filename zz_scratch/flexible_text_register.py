from .flexible_text import FlexibleText

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class FlexibleTextRegister:
    """
    Register flexible text that can either be shown or hidden simultaneously.
    """
    _target = None  # Q(Plain)TextEdit
    _visible = True  # whether the text is shown.
    _register = None  # list of FlexibleText
    show = None  # function that shows all text
    hide = None  # function that hides all text

    def __init__(self, target, visible=True):
        """
        Initialize.
        :param target: Q(Plain)TextEdit
        :param visible: whether the text should be visible by default
        :return:
        """
        self._target = target
        self._visible = visible
        self._register = list()
        if self._visible:
            self.show = self._forward('show', True)
            self.hide = self._backward('hide', False)
        else:
            self.show = self._backward('show', True)
            self.hide = self._forward('hide', False)

    @property
    def visible(self):
        """
        Check whether text is visible.
        :return: whether text is visible.
        """
        return self._visible

    @visible.setter
    def visible(self, visibility):
        """
        Set the visibility of the text.
        :param visibility: whether text should be visible.
        :return:
        """
        if visibility:
            self.show()
        else:
            self.hide()

    def insert(self, text='', cursor=None):
        """
        Insert text.
        :param text: string to be inserted.
        :param cursor: optional cursor position of insert; otherwise the current text cursor position is used.
        :return:
        """
        flex = FlexibleText(self._target, text, cursor)
        if self._visible:
            flex.show()
        self._register.append(flex)

    def _forward(self, command, visibility):
        """
        Forward traversal function for register of text.
        :param command: command to be applied to each text in the function; usually show and hide
        :param visibility: boolean to set visibility flag of the text.
        :return: A function that forward traverses all text items, applies command to each item,
         if the given visible flag is different from the current visibility of the text items and sets the
        visibility flag.
        """
        def traverse():
            if self._visible != visibility:
                for t in self._register:
                    getattr(t, command)()
                self._visible = visibility
        return traverse

    def _backward(self, command, visibility):
        """
        Backward traversal function for register of text.
        :param command: command to be applied to each text in the function; usually show and hide
        :param visibility: boolean to set visibility flag of the text.
        :return: A function that backward traverses all text items, applies command to each item,
         if the given visible flag is different from the current visibility of the text items and sets the
        visibility flag.
        """
        def traverse():
            if self._visible != visibility:
                for t in reversed(self._register):
                    getattr(t, command)()
                self._visible = visibility
        return traverse
