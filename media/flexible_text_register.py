from .flexible_text import FlexibleText

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class FlexibleTextRegister:
    """
    Register flexible text that can either be shown or hidden simultaneously.
    """
    _target = None  # Q(Plain)TextEdit
    visible = True  # whether the text is shown.
    _register = None  # list of FlexibleText
    show = None  # function that shows all text
    hide = None  # function that hides all text

    def __init__(self, target, visible=True):
        self._target = target
        self.visible =visible
        self._register = list()
        if self.visible:
            self.show = self.forward('show', True)
            self.hide = self.backward('hide', False)
        else:
            self.show = self.backward('show', True)
            self.hide = self.forward('hide', False)

    def insert(self, text='', cursor=None):
        flex = FlexibleText(self._target, text, cursor)
        if self.visible:
            flex.show()
        self._register.append(flex)

    def forward(self, command, visible):
        def over():
            for t in self._register:
                getattr(t, command)()
            self.visible = visible
        return over

    def backward(self, command, visible):
        def over():
            i = len(self._register)-1
            while i >=0:
                self._register[i].show()
                i -= 1
            self.visible = visible
        return over
