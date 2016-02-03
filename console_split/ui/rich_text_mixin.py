__author__ = 'Manfred Minimair <manfred@minimair.org>'


class RichTextMixin(object):
    def __init__(self):
        self.setAcceptRichText(False)
        self.setMouseTracking(True)
