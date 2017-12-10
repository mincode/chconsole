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


class NoRemoteConnection(Exception):
    response = ''
    status_code = 0  # http status code

    def __init__(self, response, http_code):
        super(NoRemoteConnection, self).__init__()
        self.response = response
        self.status_code = http_code


# chconnect:
class ChangeModFailed(Exception):
    file = ''

    def __init__(self, file):
        super(ChangeModFailed, self).__init__()
        self.file = file
