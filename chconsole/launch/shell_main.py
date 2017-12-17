import sys
from chconsole.launch import (
    Launch, start_console, start_chconsole, start_qtconsole
)
from chconsole.launch.launch_config import LaunchConfig
from chconsole.connect import RemoteConnector, Curie
from .gui_main import LaunchWidget, ChGuiLaunchApp

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def get():
    if len(sys.argv) > 1:
        rc = RemoteConnector(ChGuiLaunchApp.kernel_gate,
                             LaunchWidget.gate_tunnel_user,
                             Curie(sys.argv[1]))
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
        launch_config = LaunchConfig()
        launch = Launch(launch_config.kernel_gate,
                        # 'in.chgate.net', 'chconnect',
                        launch_config.gate_tunnel_user,
                        sys.argv[1])
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
