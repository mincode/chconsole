from traitlets import Bool

__author__ = 'minimair'

PROCESS_ANSI_CODES = Bool(True, config=True, help="Whether to process ANSI escape codes.")


class SignalContent:
    """
    Wrapper for data needed to output with Qt signals.
    """
    # object data
    message = None
    ansi_codes = None

    def __init__(self, message, ansi_codes=PROCESS_ANSI_CODES):
        self.message = message
        self.ansi_codes = ansi_codes


class TextSignal(SignalContent):
    pass


class HtmlSignal(SignalContent):
    pass
