from traitlets import Int
from traitlets.config.configurable import LoggingConfigurable
from .centered_text import CenteredText

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class TextRegister(LoggingConfigurable):
    """
    Register text that can either be shown or hidden simultaneously.
    """
    _target = None  # QTextDocument
    _visible = True  # whether the text is shown.
    _register = None  # list of CenteredText
    _field = 0  # length of the field to show the text.
    max_field = Int(30, help='Maximum field length')

    def __init__(self, target, visible=True, **kwargs):
        """
        Initialize.
        :param target: QTextDocument
        :param visible: whether the text should be visible by default
        :return:
        """
        super(LoggingConfigurable, self).__init__(**kwargs)
        self._target = target
        self._visible = visible
        self._register = list()

    def _update_field(self, new_field):
        """
        Update the field length.
        :param new_field: new field length; > self._field
        :return: total offset resulting from updating the field length.
        """
        new_field = min(new_field, self.max_field)
        offset = 0
        if new_field > self._field:
            if self._visible:
                for item in self._register:
                    item.shift(offset)
                    item.center(self._target, self._field, new_field)
                    offset += new_field - self._field
            self._field = new_field
        return offset

    def append(self, pos, text=''):
        """
        Append text to the register and update the field length to accommodate the string.
        :param pos: position of the text in the document; assumed to be after all other positions in the register.
        :param text: string to be inserted.
        :return:
        """
        new_text = CenteredText(pos, text)
        offset = self._update_field(len(text))
        new_text.shift(offset)
        self._register.append(new_text)
        if self._visible:
            new_text.insert(self._target, self._field)

    def show(self):
        """
        Show the text.
        :return:
        """
        if not self._visible:
            offset = 0
            for item in self._register:
                item.shift(offset)
                item.insert(self._target, self._field)
                offset += self._field
            self._visible = True

    def hide(self):
        """
        Hide the text.
        :return:
        """
        if self._visible:
            offset = 0
            for item in self._register:
                item.shift(offset)
                item.remove(self._target, self._field)
                offset -= self._field
            self._visible = False

    @property
    def viewable(self):
        """
        Check whether text is visible.
        :return: whether text is visible.
        """
        return self._visible

    @viewable.setter
    def viewable(self, new_visible):
        """
        Set the visibility of the text.
        :param new_visible: whether text should be visible.
        :return:
        """
        if new_visible:
            self.show()
        else:
            self.hide()
