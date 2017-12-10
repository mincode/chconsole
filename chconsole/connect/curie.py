__author__ = 'Manfred Minimair <manfred@minimair.org>'

import re


def _split_curie(curie=''):
    """
    Split a CURIE of the form [machine/key]. Either bracket is optional.
    :param curie: string
    :return: list of machine and key, two strings
    """

    # seperator for CURIE
    sep = '/'

    parts = curie.partition(sep)
    if parts[0] and parts[0][0] == '[':
            machine = parts[0][1:]
    else:
        machine = parts[0]
    if parts[2] and parts[2][-1] == ']':
            key = parts[2][:-1]
    else:
        key = parts[2]

    return [machine, key]


class Curie:
    """
    Curie [machine/key], where the brackets are optional.
    """
    machine = ''
    key = ''

    def __init__(self, c=''):
        """
        Init.
        :param c: curie string, allowing whitepsace on the left and right.
        """
        unpacked = _split_curie(c.lstrip().rstrip())
        self.machine = unpacked[0]
        self.key = unpacked[1]

    @classmethod
    def valid(cls, c=''):
        """
        Chack whether string contains a valid curie, allowing whitepsace on the left and right.
        @param c: string with curie.
        :return: True if string contains a valid curie.
        """
        s = c.lstrip().rstrip()
        regex = r'\A\[?[^\[/]+/[^\]]+\]?\Z'
        pattern = re.compile(regex)
        if pattern.match(s):
            return True
        else:
            return False
