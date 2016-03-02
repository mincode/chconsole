__author__ = 'Manfred Minimair <manfred@minimair.org>'


class KernelMessage:
    whole = None  # dict, kernel message
    from_here = True  # whether the message is from the current session

    def __init__(self, msg, from_here=True):
        self.whole = msg
        self.from_here = from_here

    @property
    def type(self):
        return self.whole['header']['msg_type']

    @property
    def content(self):
        return self.whole['content']
