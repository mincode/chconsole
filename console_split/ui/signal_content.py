from functools import singledispatch

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


@singledispatch
def insert_signal_content(output, target):
    raise NotImplementedError


@insert_signal_content.register(TextSignal)
def _(output, target):
    target.insertPlainText(output.content)


@insert_signal_content.register(HtmlSignal)
def _(output, target):
    target.insertHtml(output.content)
