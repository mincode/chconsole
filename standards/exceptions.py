__author__ = 'Manfred Minimair <manfred@minimair.org>'


class NoDefaultEditor(Exception):
    def __init__(self):
        super(NoDefaultEditor, self).__init__()

    def __str__(self):
        return 'NoDefaultEditor'


class CommandError(Exception):
    command = ''

    def __init__(self, command):
        super(CommandError, self).__init__()
        self.command = command
