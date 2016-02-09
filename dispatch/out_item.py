__author__ = 'Manfred Minimair <manfred@minimair.org>'


class OutItem:
    pass


class OutStream(OutItem):
    text = ''

    def __init__(self, text):
        super(OutStream, self).__init__()
        self.text = text
