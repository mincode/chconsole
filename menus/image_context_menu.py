from qtconsole.qt import QtGui
from qtconsole.svg import save_svg, svg_to_clipboard
from media import copy_image, save_image

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class ImageContextMenu(QtGui.QMenu):
    def __init__(self, parent, pos, name):
        """ Creates a context menu for the given QPoint (in widget coordinates).
        """
        super(ImageContextMenu, self).__init__(parent)

        self.addAction('Copy Image', lambda: copy_image(parent, name))
        self.addAction('Save Image As...', lambda: save_image(parent, name))
        self.addSeparator()

        svg = parent.name_to_svg_map.get(name, None)
        if svg is not None:
            self.addSeparator()
            self.addAction('Copy SVG', lambda: svg_to_clipboard(svg))
            self.addAction('Save SVG As...',
                           lambda: save_svg(svg, parent))
