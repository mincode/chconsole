from functools import singledispatch
from qtconsole.qt import QtGui, QtCore
from qtconsole.svg import svg_to_image
try:
    from IPython.lib.latextools import latex_to_png
except ImportError:
    latex_to_png = None
from messages import SvgXml, Jpeg, Png, LaTeX

__author__ = 'Manfred Minimair <manfred@minimair.org>'


svg_to_qimage = svg_to_image
# """
# Convert svg to QImage.
# :param svg: image as svg.
# :return: QImage representation of img, or raises ValueError if img cannot be converted.
# """


def jpg_to_qimage(img, metadata=None):
    return jpg_png_to_qimage(img, 'jpg', metadata)


def png_to_qimage(img, metadata=None):
    return jpg_png_to_qimage(img, 'png', metadata)


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


@singledispatch
def to_qimage(item):
    raise NotImplementedError


@to_qimage.register(SvgXml)
def _(item):
    return svg_to_qimage(item.image)


@to_qimage.register(Jpeg)
def _(item):
    return jpg_to_qimage(item.image, item.metadata)


@to_qimage.register(Png)
def _(item):
    return png_to_qimage(item.image, item.metadata)


@to_qimage.register(LaTeX)
def _(item):
    return latex_to_qimage(item.text)


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


def insert_qimage_format(cursor, format):
    """
    Insert a QImage given by a format at a cursor.
    :param cursor: QTextCursor where to insert.
    :param format: QImageFormat of the image.
    :return:
    """
    cursor.insertBlock()
    cursor.insertImage(format)
    cursor.insertBlock()


# RichJupyterWidget
def copy_image(target, name):
    """ Copies the ImageResource with 'name' to the clipboard.
    """
    image = get_image(target, name)
    QtGui.QApplication.clipboard().setImage(image)


# RichJupyterWidget
def get_image(target, name):
    """ Returns the QImage stored as the ImageResource with 'name'.
    """
    image = target.document().resource(QtGui.QTextDocument.ImageResource, QtCore.QUrl(name))
    return image


# RichJupyterWidget
def save_image(target, name, format='PNG'):
    """ Shows a save dialog for the ImageResource with 'name'.
    """
    dialog = QtGui.QFileDialog(target, 'Save Image')
    dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
    dialog.setDefaultSuffix(format.lower())
    dialog.setNameFilter('%s file (*.%s)' % (format, format.lower()))
    if dialog.exec_():
        filename = dialog.selectedFiles()[0]
        image = get_image(target, name)
        image.save(filename, format)
