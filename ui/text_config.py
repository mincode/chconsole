import sys
from traitlets.config.configurable import LoggingConfigurable
from traitlets import Integer, Unicode
from qtconsole.qt import QtGui
from qtconsole.util import get_font

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class TextConfig(LoggingConfigurable):
    """
    Mixin for configuring text properties of a QTextEdit or QPlainTextEdit.
    """
    font_family = Unicode(
        config=True,
        help="""The font family to use for the console.
        On OSX this defaults to Monaco, on Windows the default is
        Consolas with fallback of Courier, and on other platforms
        the default is Monospace.
        """)

    font_size = Integer(
        config=True, help="The font size. If unconfigured, Qt will be entrusted with the size of the font.")

    tab_width = Integer(8, config=True, help="Number of spaces used for tab.")

    def __init__(self, **kwargs):
        """
        Initialize.
        :return:
        """
        super(LoggingConfigurable, self).__init__(**kwargs)

    @staticmethod
    def _font_family_default():
        if sys.platform == 'win32':
            # Consolas ships with Vista/Win7, fallback to Courier if needed
            return 'Consolas'
        elif sys.platform == 'darwin':
            # OSX always has Monaco, no need for a fallback
            return 'Monaco'
        else:
            # Monospace should always exist, no need for a fallback
            return 'Monospace'

    def reset_font(self):
        """
        Sets the font to the default fixed-width font for this platform.
        """
        fallback = self._font_family_default()
        font = get_font(self.font_family, fallback)
        if self.font_size:
            font.setPointSize(self.font_size)
        else:
            font.setPointSize(QtGui.qApp.font().pointSize())
        font.setStyleHint(QtGui.QFont.TypeWriter)
        self._set_font(font)

    def _get_font(self):
        """ The base font being used.
        """
        return self.document().defaultFont()

    def _set_font(self, font):
        """ Sets the base font for the ConsoleWidget to the specified QFont.
        """
        font_metrics = QtGui.QFontMetrics(font)
        self.setTabStopWidth(self.tab_width * font_metrics.width(' '))

        # self._completion_widget.setFont(font)
        self.document().setDefaultFont(font)
        # if self._page_control:
        #     self._page_control.document().setDefaultFont(font)

        # self.font_changed.emit(font)

    font = property(_get_font, _set_font)
