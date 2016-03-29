__author__ = 'Manfred Minimair <manfred@minimair.org>'


class LineIter:
    """
    Iterate over the lines in a string.
    """
    lines = None  # list of lines
    index = -1  # iteration index

    def __init__(self, s):
        """
        Init.
        :param s: string with lines to be iterated over.
        :return:
        """
        self.lines = s.split('\n')

    def __iter__(self):
        """
        Iterator.
        :return: self.
        """
        return self

    def __next__(self):
        """
        Next item.
        :return: Next item in iterator or raise StopIteration.
        """
        self.index += 1
        if self.index >= len(self.lines):
            raise StopIteration
        return self.lines[self.index]
