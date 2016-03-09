__author__ = 'Manfred Minimair <manfred@minimair.org>'


class KernelMessage:
    raw = None  # dict, kernel message
    from_here = True  # whether the message is from the current session
    local_kernel = False  # whether the message is through a kernel on the local machine

    def __init__(self, msg, from_here=True, local_kernel=False):
        self.raw = msg
        self.from_here = from_here
        self.local_kernel = local_kernel

    @property
    def type(self):
        return self.raw['header']['msg_type']

    @property
    def content(self):
        return self.raw['content']
