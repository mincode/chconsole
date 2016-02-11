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


class OutItem:
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


class ClearOutput(OutItem):
    wait = False  # Wait to clear the output until new output is available

    def __init__(self, wait=False, head=True, empty=False):
        super(ClearOutput, self).__init__(head=head, empty=empty)


class OutText(OutItem):
    text = ''

    def __init__(self, text, head=True, empty=False):
        super(OutText, self).__init__(head, empty)
        self.text = text

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

    def __init__(self, text, name='stdout', head=True, empty=False):
        super(Stream, self).__init__(text, head, empty)
        self.name = name


class Input(OutText):
    execution_count = 0  # int
    local = True  # whether the input came from the local client

    def __init__(self, text, execution_count=0, local=True, head=True, empty=False):
        super(Input, self).__init__(text, head, empty)
        self.execution_count = execution_count
        self.local = local

    @property
    def code(self):
        return self.text

    def split(self, num_lines):
        count, first, rest = super(Input, self).split(num_lines)
        first.execution_count = self.execution_count
        first.local = self.local
        rest.execution_count = self.execution_count
        rest.local = self.local
        return count, first, rest
