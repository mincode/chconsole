from qtconsole.qt import QtGui, QtCore
from qtconsole.svg import svg_to_image
try:
    from IPython.lib.latextools import latex_to_png
except ImportError:
    latex_to_png = None

__author__ = 'Manfred Minimair <manfred@minimair.org>'


svg_to_qimage = svg_to_image
# """
# Convert svg to QImage.
# :param svg: image as svg.
# :return: QImage representation of img, or raises ValueError if img cannot be converted.
# """


# RichJupyterWidget, based on _insert_img
def jpg_png_to_qimage(img, fmt='png', metadata=None):
    """
    Convert jpg or png to QImage.
    :param img: image as jpg or png.
    :param fmt: 'jpg' or 'png'
    :param metadata: optional metadata dict with width and height.
    :return: QImage representation of img, or raises ValueError if img cannot be converted.
    """
    if metadata:
        width = metadata.get('width', None)
        height = metadata.get('height', None)
    else:
        width = height = None

    image = QtGui.QImage()
    image.loadFromData(img, fmt.upper())
    if width and height:
        image = image.scaled(width, height, transformMode=QtCore.Qt.SmoothTransformation)
    elif width and not height:
        image = image.scaledToWidth(width, transformMode=QtCore.Qt.SmoothTransformation)
    elif height and not width:
        image = image.scaledToHeight(height, transformMode=QtCore.Qt.SmoothTransformation)

    return image


def latex_to_qimage(text):
    png = latex_to_png(text)
    return jpg_png_to_qimage(png, 'png')


# RichJupyterWidget add_image
def register_qimage(document, image):
    """ Adds the specified QImage to the document and returns a
        QTextImageFormat that references it.
    """
    name = str(image.cacheKey())
    document.addResource(QtGui.QTextDocument.ImageResource,
                         QtCore.QUrl(name), image)
    img_format = QtGui.QTextImageFormat()
    img_format.setName(name)
    return img_format


def insert_qimage_format(cursor, fmt):
    """
    Insert a QImage given by a format at a cursor.
    :param cursor: QTextCursor where to insert.
    :param fmt: QImageFormat of the image.
    :return:
    """
    cursor.insertBlock()
    cursor.insertImage(format)
    cursor.insertBlock()
