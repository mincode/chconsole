from traitlets import Bool, Unicode
from traitlets.config.configurable import LoggingConfigurable
from qtconsole.util import MetaQObjectHasTraits
from qtconsole.qt import QtGui

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def pager_template(edit_class):
    class Pager(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, edit_class), {})):
        """
        The pager of the console.
        """
        location = Unicode('')
        # The type of paging to use.

        _is_shown = Bool(False)
        # True if the pager is supposed to be shown. Allows for correct application of the traitlets location
        # change handler when the container widget is still being constructed and the pager is set to be shown,
        # however, is not yet visible.

        _locations = {}  # Possible pager locations

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
            LoggingConfigurable.__init__(self, **kwargs)
            self._locations = dict(locations)
            self.location = initial_location

        # Traitlets handler
        def _location_changed(self, changed=None):
            """
            Set the pager at a location, initially or upon change of location
            :param location: Location to set the pager
            :return:
            """
            is_shown = self._is_shown or self.isVisible()
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
            self._is_shown = True

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
            self._is_shown = False

    return Pager
