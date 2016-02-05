__author__ = 'minimair'


class Source:
    """
    Wrapper for source code to ge executed.
    """
    # object data
    code = None  # str
    hidden = False  # Bool

    def __init__(self, code, hidden=False):
        self.code = code
        self.hidden = hidden

