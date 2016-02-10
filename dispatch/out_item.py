__author__ = 'Manfred Minimair <manfred@minimair.org>'


class OutItem:
    head = True
    # True if this is the beginning of a new item for output.
    # False if this is a part of the item previously sent to output.

    def split(self):
        pass


class OutStream(OutItem):
    """

    """
    text = ''

    def __init__(self, text):
        super(OutStream, self).__init__()
        self.text = text
