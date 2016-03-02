from .kernel_message import KernelMessage

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Message(object):
    kernel_message = None  # KernelMessage
    show_other = True  # whether the current client wants to show other clients' messages
    ansi_codes = True  # whether the current client should process ansi codes

    def __init__(self, kernel_message, show_other=True, ansi_codes=True):
        """
        Initialize.
        :param msg: KernelMessage
        :return:
        """
        self.kernel_message = kernel_message
        self.show_other = show_other
        self.ansi_codes = ansi_codes

    @property
    def whole(self):
        return self.kernel_message.whole

    @property
    def from_here(self):
        return self.kernel_message.from_here

    @property
    def show_me(self):
        """
        Determine if message is to be shown.
        :return: True if message is to be shown.
        """
        return self.kernel_message.from_here or self.show_other

    @property
    def type(self):
        return self.kernel_message.whole['header']['msg_type']

    @property
    def content(self):
        return self.kernel_message.whole.get('content', '')
