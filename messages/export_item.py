__author__ = 'Manfred Minimair <manfred@minimair.org>'


class ExportItem:
    def __init__(self):
        pass

    @property
    def type(self):
        return type(self).__name__.lower()


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


class Exit(ExportItem):
    keep_kernel = True  # whether to keep the kernel on exit

    def __init__(self, keep_kernel=True):
        super(Exit, self).__init__()
        self.keep_kernel = keep_kernel
