from standards import Importable

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


class ImportItem(Importable):
    @property
    def type(self):
        return type(self).__name__


################################################################################################
# TabContent
class ClearAll(ImportItem):
    """
    Clear all widgets.
    """
    pass


class ExitRequested(ImportItem):
    keep_kernel_on_exit = False  # keep kernel when exit main widget
    confirm = False  # whether exit should be confirmed from the user

    def __init__(self, keep_kernel_on_exit, confirm=False):
        super(ExitRequested, self).__init__()
        self.keep_kernel_on_exit = keep_kernel_on_exit
        self.confirm = confirm


class EditFile(ImportItem):
    filename = ''
    line_number = None  # line number

    def __init__(self, filename, line_number=None):
        super(EditFile, self).__init__()
        self.filename = filename
        self.line_number = line_number


class InputRequest(ImportItem):
    prompt = ''  # prompt to show on input request
    password = False  # whether the request is for a password; if True the input should not be echoed

    def __init__(self, prompt='', password=False):
        super(InputRequest, self).__init__()
        self.prompt = prompt
        self.password = password


################################################################################################
# Entry
class InText(ImportItem):
    """
    Text to be posted in input area.
    """
    text = ''

    def __init__(self, text=''):
        super(InText, self).__init__()
        self.text = text


class CompleteItems(ImportItem):
    """
    Items used for code completion.
    """
    matches = None  # list of items that match for completion
    start = 0  # start position of cursor
    end = 0  # end position of cursor where to complete

    def __init__(self, matches, start=0, end=0):
        super(CompleteItems, self).__init__()
        self.matches = matches
        self.start = start
        self.end = end


class CallTip(ImportItem):
    """
    Call tips.
    """
    content = None  # content of the call tip reply message

    def __init__(self, content):
        super(CallTip, self).__init__()
        self.content = content


################################################################################################
# Pager
class SplitItem(ImportItem):
    def __init__(self):
        super(SplitItem, self).__init__()

    def split(self, num_lines):
        """

        :param num_lines:
        :return:
        """
        if num_lines <= 0:
            count = 0
            first_item = None
            rest_item = self
        else:
            count = 1
            first_item = self
            rest_item = None
        return count, first_item, rest_item


class AtomicText(SplitItem):
    text = ''
    ansi_codes = True  # whether text has ansi_codes

    def __init__(self, text='', ansi_codes=True):
        super(AtomicText, self).__init__()
        self.text = text
        self.ansi_codes = ansi_codes


class SplitText(AtomicText):
    def __init__(self, text='', ansi_codes=True):
        super(SplitText, self).__init__(text=text, ansi_codes=ansi_codes)

    def split(self, num_lines):
        """
        Split text item into initial piece of given number of lines and the rest.
        :param num_lines: number of lines for the initial piece.
        :return: number of lines in the initial piece, item of initial piece, item of rest,
                    where head property of rest is false in rest. The rest is None if
                    it is empty.
        """
        count, first_text, rest_text = _split_lines(num_lines, self.text)
        first = type(self)(text=first_text, ansi_codes=self.ansi_codes)
        rest = type(self)(text=rest_text, ansi_codes=self.ansi_codes) if rest_text else None
        return count, first, rest


class HtmlText(AtomicText):
    def __init__(self, text=''):
        super(HtmlText, self).__init__(text=text, ansi_codes=False)


class Stream(SplitItem):
    clearable = True  # True if text can be cleared by ClearOutput
    content = None  # AtomicText, SplitText, HtmlText

    def __init__(self, content=None, clearable=True):
        super(Stream, self).__init__()
        self.clearable = clearable
        if isinstance(content, str):
            self.content = SplitText(content)
        else:
            self.content = content

    @property
    def ansi_codes(self):
        if hasattr(self.content, 'ansi_codes'):
            return self.content.ansi_codes
        else:
            return False

    @ansi_codes.setter
    def ansi_codes(self, ansi_codes):
        if hasattr(self.content, 'ansi_codes'):
            self.content.ansi_codes = ansi_codes

    def split(self, num_lines):
        """
        Split text item into initial piece of given number of lines and the rest.
        :param num_lines: number of lines for the initial piece.
        :return: number of lines in the initial piece, item of initial piece, item of rest,
                    where head property of rest is false in rest. The rest has head False and empty is set if
                    it is empty.
        """
        count, first, rest = self.content.split(num_lines)
        first_stream = type(self)(content=first, clearable=self.clearable)
        rest_stream = type(self)(content=rest, clearable=self.clearable) if rest else None
        return count, first_stream, rest_stream


class Stdout(Stream):
    def __init__(self, content=None, clearable=True):
        super(Stdout, self).__init__(content=content, clearable=clearable)


class PageDoc(SplitItem):
    text_stream = None  # text version of text if available
    html_stream = None  # html version of text if available

    def __init__(self, text='', html=''):
        super(PageDoc, self).__init__()
        self.text_stream = Stdout(SplitText(text), clearable=False)
        if html:
            self.html_stream = Stdout(HtmlText(html), clearable=False)

    @property
    def ansi_codes(self):
        if self.text_stream:
            return self.text_stream.ansi_codes
        else:
            return False

    @ansi_codes.setter
    def ansi_codes(self, ansi_codes):
        if self.text_stream:
            self.text_stream.ansi_codes = ansi_codes


################################################################################################
# Receiver
class Stderr(Stream):
    def __init__(self, content=None, clearable=False):
        super(Stderr, self).__init__(content=content, clearable=clearable)


class ClearOutput(SplitItem):
    wait = False  # Wait to clear the output until new output is available

    def __init__(self, wait=False):
        super(ClearOutput, self).__init__()
        self.wait = wait

    def split(self, num_lines):
        """
        Split text item into initial piece of given number of lines and the rest.
        :param num_lines: number of lines for the initial piece.
        :return: number of lines in the initial piece, item of initial piece, item of rest,
                    where head property of rest is false in rest. The rest has head False and empty is set if
                    it is empty.
        """
        count, first, rest = super(ClearOutput, self).split(num_lines)
        if first:
            first.wait = self.wait
        if rest:
            rest.wait = self.wait
        return count, first, rest


class Banner(Stdout):
    help_links = None  # list of dict: ('text', 'url')

    def __init__(self, content='', help_links=None, clearable=False):
        new_content = AtomicText(content) if isinstance(content, str) else content
        super(Banner, self).__init__(content=new_content, clearable=clearable)
        self.help_links = help_links

    @property
    def stream(self):
        return Stdout(content=self.content, clearable=self.clearable)

    def split(self, num_lines):
        """
        Split text item into initial piece of given number of lines and the rest.
        :param num_lines: number of lines for the initial piece.
        :return: number of lines in the initial piece, item of initial piece, item of rest,
                    where head property of rest is false in rest. The rest has head False and empty is set if
                    it is empty.
        """
        count, first, rest = super(Banner, self).split(num_lines)
        if rest:
            rest.help_links = self.help_links
        elif first:
            first.help_links = self.help_links
        return count, first, rest


class Execution(Stream):
    execution_count = 0  # int

    def __init__(self, content='', execution_count=0, ansi_codes=False, clearable=False):
        new_content = SplitText(text=content, ansi_codes=ansi_codes) if isinstance(content, str) else content
        super(Execution, self).__init__(content=new_content, clearable=clearable)
        self.execution_count = execution_count

    def split(self, num_lines):
        count, first, rest = super(Execution, self).split(num_lines)
        if first:
            first.execution_count = self.execution_count
        if rest:
            rest.execution_count = self.execution_count
        return count, first, rest


class Input(Execution):
    def __init__(self, content='', execution_count=0, clearable=False):
        super(Input, self).__init__(content, execution_count=execution_count, ansi_codes=True, clearable=clearable)

    @property
    def code(self):
        return self.content.text


class Result(Execution):
    def __init__(self, content='', execution_count=0, clearable=False):
        super(Result, self).__init__(content, execution_count=execution_count, clearable=clearable)
