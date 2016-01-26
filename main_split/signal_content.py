__author__ = 'minimair'


class SignalContent:
    """
    Wrapper for data needed to output with Qt signals.
    """
    content = None

    def __init__(self, content):
        self.content = content


class TextSignal(SignalContent):
    pass

class HtmlSignal(SignalContent):
    pass
