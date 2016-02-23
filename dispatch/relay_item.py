__author__ = 'Manfred Minimair <manfred@minimair.org>'


def _split_lines(num_lines, text):
    """
    Split text into initial piece of given number of lines and the rest. The last line in text does not need to be
    terminated with '\n'. An empty text counts as one line.
    :param num_lines: number of lines for the initial piece.
    :param text: string to be split.
    :return: count of number of lines in the initial piece, string of initial piece, rest string.
    """
    num_lines = 0 if num_lines < 0 else num_lines
    count = 0
    location = 0
    while count < num_lines:
        location = text.find('\n', location) + 1  # location after '\n'
        count += 1
        if location == 0:  # less lines than num_lines
            return count, text, ''
    return num_lines, text[:location], text[location:]


class RelayItem:
    head = True
    # True if this is the beginning of a new item for output.
    # False if this is a part of the item previously sent to output.
    empty = False
    # whether item is considered to be empty

    def __init__(self, head=True, empty=False):
        self.head = head
        self.empty = empty

    def split(self, num_lines):
        """

        :param num_lines:
        :return:
        """
        if num_lines <= 0:
            count = 0
            first_item = type(self)(head=self.head, empty=True)
            rest_item = self
            rest_item.head = False
        else:
            count = 1
            first_item = self
            rest_item = type(self)(head=False, empty=True)
        return count, first_item, rest_item


class ClearOutput(RelayItem):
    wait = False  # Wait to clear the output until new output is available

    def __init__(self, wait=False, head=True, empty=False):
        super(ClearOutput, self).__init__(head=head, empty=empty)
        self.wait = wait


class OutText(RelayItem):
    text = ''
    ansi_codes = True  # whether text has ansi_codes

    def __init__(self, text='', head=True, empty=False, ansi_codes=True):
        super(OutText, self).__init__(head=head, empty=empty)
        self.text = text
        self.ansi_codes = ansi_codes

    def split(self, num_lines):
        """
        Split text item into initial piece of given number of lines and the rest.
        :param num_lines: number of lines for the initial piece.
        :return: number of lines in the initial piece, item of initial piece, item of rest,
                    where head property of rest is false in rest. The rest has head False and empty is set if
                    it is empty.
        """
        count, first_text, rest_text = _split_lines(num_lines, self.text)
        first = type(self)(first_text, head=self.head, empty=self.empty)
        rest = type(self)(rest_text, head=False, empty=(len(rest_text) == 0))
        return count, first, rest


class Stream(OutText):
    name = 'stdout'  # name of the stream
    clearable = True  # True if text can be cleared by ClearOutput

    def __init__(self, text='', name='stdout', clearable=True, head=True, empty=False, ansi_codes=True):
        super(Stream, self).__init__(text=text, head=head, empty=empty)
        self.name = name
        self.clearable = clearable
        self.ansi_codes = ansi_codes


class Banner(Stream):
    def __init__(self, text='', head=True, empty=False, ansi_codes=True):
        super(Banner, self).__init__(text=text, name='stdout', clearable=False, head=head, empty=empty,
                                     ansi_codes=ansi_codes)

    @property
    def stream(self):
        return Stream(text=self.text, name='stdout', clearable=self.clearable, head=self.head, empty=self.empty,
                      ansi_codes=self.ansi_codes)


class PageDoc(Stream):
    html = ''  # html version of text if available

    def __init__(self, text='', head=True, empty=False, ansi_codes=True, html=''):
        super(PageDoc, self).__init__(
            text=text, name='stdout', clearable=False, head=head, empty=empty, ansi_codes=ansi_codes)
        self.html = html


class ExecuteText(OutText):
    execution_count = 0  # int

    def __init__(self, text='', execution_count=0, head=True, empty=False, ansi_codes=True):
        super(ExecuteText, self).__init__(text=text, head=head, empty=empty)
        self.execution_count = execution_count
        self.ansi_codes = ansi_codes

    def split(self, num_lines):
        count, first, rest = super(ExecuteText, self).split(num_lines)
        first.execution_count = self.execution_count
        rest.execution_count = self.execution_count
        return count, first, rest


class Input(ExecuteText):
    def __init__(self, text='', execution_count=0, head=True, empty=False, ansi_codes=True):
        super(Input, self).__init__(
            text=text, execution_count=execution_count, head=head, empty=empty, ansi_codes=ansi_codes)

    @property
    def code(self):
        return self.text


class ExecuteResult(ExecuteText):
    def __init__(self, text='', execution_count=0, head=True, empty=False, ansi_codes=False):
        super(ExecuteResult, self).__init__(
            text=text, execution_count=execution_count, head=head, empty=empty, ansi_codes=ansi_codes)


class EditFile(RelayItem):
    filename = ''
    line_number = None  # line number

    def __init__(self, filename, line_number=None, head=True, empty=False):
        super(EditFile, self).__init__(head=head, empty=empty)
        self.filename = filename
        self.line_number = line_number


class ExitRequested(RelayItem):
    keep_kernel_on_exit = False  # keep kernel when exit main widget

    def __init__(self, keep_kernel_on_exit, head=True, empty=False):
        super(ExitRequested, self).__init__(head=head, empty=empty)
        self.keep_kernel_on_exit = keep_kernel_on_exit


class InText(RelayItem):
    text = ''

    def __init__(self, text='', head=True, empty=False):
        super(InText, self).__init__(head=head, empty=empty)
        self.text = text


class InputRequest(OutText):
    password = False  # whether the request is for a password; if True the input should not be echoed

    def __init__(self, text='', password=False, head=True, empty=False, ansi_codes=True):
        super(InputRequest, self).__init__(text=text, head=head, empty=empty)
        self.password = password
        self.ansi_codes = ansi_codes

    @property
    def prompt(self):
        return self.text

    # input request splits into stream out + input request
