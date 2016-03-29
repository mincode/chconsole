__author__ = 'Manfred Minimair <manfred@minimair.org>'


class ExportItem:
    pass


class Interrupt(ExportItem):
    pass


class Exit(ExportItem):
    keep_kernel = True  # whether to keep the kernel on exit

    def __init__(self, keep_kernel=True):
        super(Exit, self).__init__()
        self.keep_kernel = keep_kernel


class Restart(ExportItem):
    clear = True  # whether to clear on restart

    def __init__(self, clear=True):
        super(Restart, self).__init__()
        self.clear = clear


class UserInput(ExportItem):
    """
    User input given to an input request from the kernel.
    """
    text = ''  # user input as text

    def __init__(self, text=''):
        super(UserInput, self).__init__()
        self.text = text


class TailHistory(ExportItem):
    """
    Tail history request.
    """
    length = 1000  # last length history items

    def __init__(self, length=1000):
        super(TailHistory, self).__init__()
        self.length = length


class Code(ExportItem):
    source = None  # Source

    def __init__(self, source):
        super(Code, self).__init__()
        self.source = source


class Execute(Code):
    pass


class CodeFragment(Code):
    position = 0  # int

    def __init__(self, source, position):
        super(CodeFragment, self).__init__(source)
        self.position = position


class Inspect(CodeFragment):
    pass


class Complete(CodeFragment):
    pass
