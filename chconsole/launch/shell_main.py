import sys
from chconsole.launch import (
    Launch, start_console, start_chconsole, start_qtconsole
)
from chconsole.connect import RemoteConnector, Curie

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def get():
    if len(sys.argv) > 1:
        rc = RemoteConnector(Curie(sys.argv[1]))
        print(rc.info)
    else:
        print('Need to provide curie [machine/key] on the command line.')


def _launch(console_fun):
    """
    Launch with a given console function.
    :param console_fun: console_fun(Launch instance) launches the console.
    :return:
    """
    if len(sys.argv) > 1:
        launch = Launch(sys.argv[1])
        console_fun(launch)
    else:
        print('Need to provide curie [machine/key] on the command line.')


def console():
    _launch(start_console)


def qtconsole():
    _launch(start_qtconsole)


def chconsole():
    _launch(start_chconsole)


if __name__ == '__main__':
    _launch(start_console)
