from traitlets import Unicode
from qtconsole.util import MetaQObjectHasTraits
from qtconsole.qt import QtGui, QtCore
from .text_config import TextConfig
from .standard_filters import ViewportFilter, TextAreaFilter
from .pager_filter import PagerFilter

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def pager_template(edit_class):
    class Pager(MetaQObjectHasTraits('NewBase', (TextConfig, edit_class), {})):
        """
        The pager of the console.
        """
        location = Unicode('')
        # The type of paging to use.

        _locations = {}  # Possible pager locations

        pager_scroll_events = None  # list of admissible scroll events for the pager
        viewport_filter = None
        pager_filter = None
        text_area_filter = None
        release_focus = QtCore.Signal()

        def __init__(self, locations, initial_location, text='', parent=None, **kwargs):
            """
            Initialize pager.
            :param locations: Possible pager locations,
                                list of pairs (location, {'target': QSplitter or QStackedLayout, 'index': Integer}),
                                where location is Enum('top', 'inside', 'right') indicating the loation of the pager,
                                target is the container where the pager is placed and index is its index in the
                                container.
            :param text: To initialize the pager with.
            :param parent: Parent widget.
            :param kwargs: Passed to LoggingConfigurable.
            :return:
            """
            QtGui.QTextEdit.__init__(self, text, parent)
            TextConfig.__init__(self, **kwargs)
            self._locations = dict(locations)
            self.location = initial_location
            self.document().setMaximumBlockCount(0)

            # While scrolling the pager on Mac OS X, it tears badly.  The
            # NativeGesture is platform and perhaps build-specific hence
            # we take adequate precautions here.
            self.pager_scroll_events = [QtCore.QEvent.Wheel]
            if hasattr(QtCore.QEvent, 'NativeGesture'):
                self.pager_scroll_events.append(QtCore.QEvent.NativeGesture)

            self.viewport_filter = ViewportFilter(self)
            self.viewport().installEventFilter(self.viewport_filter)
            self.pager_filter = PagerFilter(self)
            self.installEventFilter(self.pager_filter)
            self.text_area_filter = TextAreaFilter(self)
            self.installEventFilter(self.text_area_filter)

        # Traitlets handler
        def _location_changed(self, changed=None):
            """
            Set the pager at a location, initially or upon change of location
            :param location: Location to set the pager
            :return:
            """
            is_shown = self.isVisible()
            self.setParent(None)  # ensure page is not contained in any of its containers
            target = self._locations[self.location]['target']
            index = self._locations[self.location]['index']
            target.insertWidget(index, self)
            if is_shown:
                self.show()

        def show(self):
            """
            Show the pager.
            :return:
            """
            target = self._locations[self.location]['target']
            if isinstance(target, QtGui.QStackedLayout):
                target.setCurrentWidget(self)
            super(edit_class, self).show()

        def hide(self):
            """
            Hide the pager.
            :return:
            """
            target = self._locations[self.location]['target']
            if isinstance(target, QtGui.QStackedLayout):
                index = self._locations[self.location]['index']
                target.setCurrentIndex((index+1) % target.count())
            super(edit_class, self).hide()

        def post(self, item):
            self.clear()
            if hasattr(self, 'insertHtml') and item.html != '':
                self.insert_html(item.html)
            else:
                self.insert_ansi_text(item.text)
            self.moveCursor(QtGui.QTextCursor.Start)
            self.setFocus()
            self.show()

    return Pager
