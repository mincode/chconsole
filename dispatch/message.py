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


class Message(KernelMessage):
    show_other = True  # whether the current client wants to show other clients' messages
    ansi_codes = True  # whether the current client should process ansi codes

    def __init__(self, msg):
        self.whole = msg.whole
        self.from_here = msg.from_here

    @property
    def show_me(self):
        """
        Determine if message is to be shown.
        :return: True if message is to be shown.
        """
        return self.from_here or self.show_other

    @property
    def type(self):
        return self.whole['header']['msg_type']

    @property
    def content(self):
        return self.whole.get('content', '')
