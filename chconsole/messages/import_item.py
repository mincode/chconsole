from functools import singledispatch

from chconsole.media import svg_to_qimage, jpg_to_qimage, png_to_qimage, latex_to_qimage
from chconsole.standards import Importable

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
    username = ''

    def __init__(self, username=''):
        super(ImportItem, self).__init__()
        self.username = username

    @property
    def type(self):
        return type(self).__name__


################################################################################################
# Meta in TabContent
class UserJoin(ImportItem):
    """
    A user joins.
    """
    client_id = ''  # unique id of joining user client

    def __init__(self, client_id='', username=''):
        """
        Initialize.
        :param client_id: id of the client to join.
        :param username: user name to join.
        """
        super(UserJoin, self).__init__(username=username)
        self.client_id = client_id


class UserName(ImportItem):
    """
    Name of the current user.
    """
    session = ''  # current session id
    client_id = ''  # id of the current client which sends its user name
    to_who_client_id = ''  # unique id of the client to who to send the name of the current user
    to_who = ''  # name of the user to who to send the current user name

    def __init__(self, session='', client_id='', username='', to_who_client_id='', to_who=''):
        """
        Initizlize.
        :param session: current session id.
        :param client_id: id of the client which sends its user name.
        :param username: user name to be sent.
        :param to_who_client_id: id of client to who to send the user name.
        :param to_who: name of user to who to send the user name.
        """
        super(UserName, self).__init__(username=username)
        self.session = session
        self.client_id = client_id
        self.to_who_client_id = to_who_client_id
        self.to_who = to_who


class UserLeave(ImportItem):
    """
    A user leaves.
    """
    client_id = ''  # unique id of this client

    def __init__(self, client_id='', username=''):
        """
        Initialize.
        :param client_id: id of the client to leave.
        :param username: user name to leave.
        """
        super(UserLeave, self).__init__(username=username)
        self.client_id = client_id


################################################################################################
# TabContent
class ClearAll(ImportItem):
    """
    Clear all widgets.
    """
    pass


class ClearCurrentEntry(ImportItem):
    """
    Clear current entry widget.
    """
    pass


class History(ImportItem):
    """
    History list.
    """
    items = None  # history items

    def __init__(self, items, username=''):
        super(History, self).__init__(username=username)
        self.items = items


class ExitRequested(ImportItem):
    keep_kernel_on_exit = False  # keep kernel when exit main widget
    confirm = False  # whether exit should be confirmed from the user

    def __init__(self, keep_kernel_on_exit, confirm=False, username=''):
        super(ExitRequested, self).__init__(username=username)
        self.keep_kernel_on_exit = keep_kernel_on_exit
        self.confirm = confirm


class EditFile(ImportItem):
    filename = ''
    line_number = None  # line number

    def __init__(self, filename, line_number=None, username=''):
        super(EditFile, self).__init__(username=username)
        self.filename = filename
        self.line_number = line_number


class InputRequest(ImportItem):
    prompt = ''  # prompt to show on input request
    password = False  # whether the request is for a password; if True the input should not be echoed

    def __init__(self, prompt='', password=False, username=''):
        super(InputRequest, self).__init__(username=username)
        self.prompt = prompt
        self.password = password


################################################################################################
# Entry
class InText(ImportItem):
    """
    Text to be posted in input area.
    """
    text = ''

    def __init__(self, text='', username=''):
        super(InText, self).__init__(username=username)
        self.text = text


class CompleteItems(ImportItem):
    """
    Items used for code completion.
    """
    matches = None  # list of items that match for completion
    start = 0  # start position of cursor
    end = 0  # end position of cursor where to complete

    def __init__(self, matches, start=0, end=0, username=''):
        super(CompleteItems, self).__init__(username=username)
        self.matches = matches
        self.start = start
        self.end = end


class CallTip(ImportItem):
    """
    Call tips.
    """
    content = None  # content of the call tip reply message

    def __init__(self, content=None, username=''):
        super(CallTip, self).__init__(username=username)
        self.content = content


################################################################################################
# Stream content: choice of different media formats
# AtomicText, SplitText, HtmlText, SvgXml, Jpeg, Png, LaTeX
# The stream content can either be one of these, or a list representing a choice.
# By default SplitText
class SplitItem(ImportItem):
    def __init__(self, username=''):
        super(SplitItem, self).__init__(username=username)

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

    def __init__(self, text='', ansi_codes=True, username=''):
        super(AtomicText, self).__init__(username=username)
        self.text = text
        self.ansi_codes = ansi_codes


class SplitText(AtomicText):
    def __init__(self, text='', ansi_codes=True, username=''):
        super(SplitText, self).__init__(text=text, ansi_codes=ansi_codes, username=username)

    def split(self, num_lines):
        """
        Split text item into initial piece of given number of lines and the rest.
        :param num_lines: number of lines for the initial piece.
        :return: number of lines in the initial piece, item of initial piece, item of rest,
                    where head property of rest is false in rest. The rest is None if
                    it is empty.
        """
        count, first_text, rest_text = _split_lines(num_lines, self.text)
        first = type(self)(text=first_text, ansi_codes=self.ansi_codes, username=self.username)
        rest = type(self)(text=rest_text, ansi_codes=self.ansi_codes, username=self.username) if rest_text else None
        return count, first, rest


class HtmlText(AtomicText):
    def __init__(self, text='', username=''):
        super(HtmlText, self).__init__(text=text, ansi_codes=False, username=username)


class Image(SplitItem):
    image = None   # the image
    metadata = None  # metadata on the image such as dimensions

    def __init__(self, image, metadata=None, username=''):
        super(Image, self).__init__(username=username)
        self.image = image
        self.metadata = metadata


class SvgXml(Image):
    pass


class Png(Image):
    pass


class Jpeg(Image):
    pass


class LaTeX(AtomicText):
    """
    LaTeX text.
    """
    def __init__(self, text, username=''):
        super(LaTeX, self).__init__(text, ansi_codes=False, username=username)


class Content(SplitItem):
    data = None  # list of SplitItem

    def __init__(self, first=None, username=''):
        super(Content, self).__init__(username=username)
        self.data = list()
        if first is not None:
            self.data.append(first)

    def append(self, item):
        self.data.append(item)

    @property
    def text(self):
        for item in self.data:
            if hasattr(item, 'text'):
                return item.text
        return ''

    @text.setter
    def text(self, text):
        for item in self.data:
            if hasattr(item, 'text'):
                item.text = text

    @property
    def ansi_codes(self):
        for item in self.data:
            if hasattr(item, 'ansi_codes'):
                return item.ansi_codes
        return False

    def split(self, num_lines):
        count_max = 0
        first_content = Content(username=self.username)
        rest_content = Content(username=self.username)
        for item in self.data:
            if item:
                count, first, rest = item.split(num_lines)
                count_max = max(count_max, count)
                if first:
                    first_content.data.append(first)
                if rest:
                    rest_content.data.append(rest)
        if not first_content:
            first_content = None
        if not rest_content.data:
            # nothing in rest_content
            rest_content = None

        return count_max, first_content, rest_content

    def get(self, class_names):
        """
        Return an item of a specific class.
        :param class_names: class name or tuple of class names.
        :return: the first item matching class_names or None.
        """
        for item in self.data:
            if isinstance(item, class_names):
                return item
        return None


class Stream(SplitItem):
    clearable = True  # True if text can be cleared by ClearOutput
    content = None  # AtomicText, SplitText, HtmlText

    def __init__(self, content=None, clearable=True, username=''):
        super(Stream, self).__init__(username=username)
        self.clearable = clearable
        if isinstance(content, str):
            self.content = Content(SplitText(content, username=username), username=username)
        elif isinstance(content, Content):
            self.content = content
        else:
            self.content = Content(content, username=username)

    @property
    def ansi_codes(self):
        return self.content.ansi_codes

    @ansi_codes.setter
    def ansi_codes(self, x):
        if hasattr(self.content, 'ansi_codes'):
            self.content.ansi_codes = x

    def split(self, num_lines):
        """
        Split text item into initial piece of given number of lines and the rest.
        :param num_lines: number of lines for the initial piece.
        :return: number of lines in the initial piece, item of initial piece, item of rest,
                    where head property of rest is false in rest. The rest has head False and empty is set if
                    it is empty.
        """
        if self.content:
            count, first, rest = self.content.split(num_lines)
        else:
            count, first, rest = 0, None, None
        first_stream = type(self)(content=first, clearable=self.clearable, username=self.username)
        rest_stream = type(self)(content=rest, clearable=self.clearable, username=self.username) if rest else None
        return count, first_stream, rest_stream


class Stdout(Stream):
    def __init__(self, content=None, clearable=True, username=''):
        super(Stdout, self).__init__(content=content, clearable=clearable, username=username)


################################################################################################
# Pager
class PageDoc(SplitItem):
    text_stream = None  # text version of text if available
    html_stream = None  # html version of text if available

    def __init__(self, text='', html='', username=''):
        super(PageDoc, self).__init__(username=username)
        self.text_stream = Stdout(SplitText(text, username=username), clearable=False, username=username)
        if html:
            self.html_stream = Stdout(HtmlText(html, username=username), clearable=False, username=username)

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
    def __init__(self, content=None, clearable=False, username=''):
        super(Stderr, self).__init__(content=content, clearable=clearable, username=username)


class ClearOutput(SplitItem):
    wait = False  # Wait to clear the output until new output is available

    def __init__(self, wait=False, username=''):
        super(ClearOutput, self).__init__(username=username)
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

    def __init__(self, content='', help_links=None, clearable=False, username=''):
        new_content = AtomicText(content, username=username) if isinstance(content, str) else content
        super(Banner, self).__init__(content=new_content, clearable=clearable, username=username)
        self.help_links = help_links

    @property
    def stream(self):
        return Stdout(content=self.content, clearable=self.clearable, username=self.username)

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

    def __init__(self, content='', execution_count=0, ansi_codes=False, clearable=False, username=''):
        new_content = SplitText(text=content, ansi_codes=ansi_codes, username=username) \
            if isinstance(content, str) else content
        super(Execution, self).__init__(content=new_content, clearable=clearable, username=username)
        self.execution_count = execution_count

    def split(self, num_lines):
        count, first, rest = super(Execution, self).split(num_lines)
        if first:
            first.execution_count = self.execution_count
        if rest:
            rest.execution_count = self.execution_count
        return count, first, rest


class Input(Execution):
    def __init__(self, content='', execution_count=0, clearable=False, username=''):
        super(Input, self).__init__(content, execution_count=execution_count, ansi_codes=True, clearable=clearable,
                                    username=username)

    @property
    def code(self):
        return self.content.text


class Result(Execution):
    def __init__(self, content=None, execution_count=0, clearable=False, username=''):
        super(Result, self).__init__(content, execution_count=execution_count, clearable=clearable, username=username)


@singledispatch
def to_qimage(item):
    raise NotImplementedError


@to_qimage.register(SvgXml)
def _(item):
    return svg_to_qimage(item.image)


@to_qimage.register(Jpeg)
def _(item):
    return jpg_to_qimage(item.image, item.metadata)


@to_qimage.register(Png)
def _(item):
    return png_to_qimage(item.image, item.metadata)


@to_qimage.register(LaTeX)
def _(item):
    return latex_to_qimage(item.text)
