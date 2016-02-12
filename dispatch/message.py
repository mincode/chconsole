__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Message:
    msg = None  # dict, kernel message
    from_here = True  # whether the message is from the current client
    show_other = True  # whether the current client wants to show other clients' messages

    def __init__(self, msg, from_here=True, show_other=True):
        self.msg = msg
        self.from_here = from_here
        self.show_other = show_other

    @property
    def show_me(self):
        """
        Determine if message is to be shown.
        :return: True if message is to be shown.
        """
        return self.from_here or self.show_other

    @property
    def type(self):
        return self.msg['header']['msg_type']

    @property
    def content(self):
        return self.msg['content']
