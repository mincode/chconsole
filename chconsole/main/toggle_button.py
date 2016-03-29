from qtconsole.qt import QtCore, QtGui

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class ToggleButton(QtGui.QToolButton):
    text = ''
    checked_tooltip = ''
    unchecked_tooltip = ''
    checked_color = None
    unchecked_color = None
    partner = None

    def __init__(self, parent=None):
        super(ToggleButton, self).__init__(parent)

    def initialize(self, is_checked, text, checked_tooltip, unchecked_tooltip, checked_color, partner):
        self.setCheckable(True)
        self.setChecked(is_checked)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.text = text
        self.setText(self.text)
        self.checked_tooltip = checked_tooltip
        self.unchecked_tooltip = unchecked_tooltip
        self.setAutoFillBackground(True)
        self.unchecked_color = self.palette().color(self.backgroundRole())
        self.checked_color = checked_color
        self.partner = partner
        self.set_activation(self.isChecked())
        self.toggled.connect(self._on_toggled)

    def set_activation(self, checked):
        if checked:
            new_tooltip = self.checked_tooltip
            new_color = self.checked_color
        else:
            new_tooltip = self.unchecked_tooltip
            new_color = self.unchecked_color

        self.setToolTip(new_tooltip)
        new_palette = self.palette()
        new_palette.setColor(self.backgroundRole(), new_color)
        self.setPalette(new_palette)

    # Slot
    def _on_toggled(self, checked):
        if checked == self.partner.isChecked():
            self.partner.toggle()
        self.set_activation(checked)
