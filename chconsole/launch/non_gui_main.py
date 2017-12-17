import sys
from chconsole.launch import (
    Launch, start_console, start_chconsole, start_qtconsole
)
from chconsole.launch.launch_config import LaunchConfig
from chconsole.connect import RemoteConnector, Curie

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def get(launch_config):
    """
    :param launch_config: LaunchConfig.
    """
    if len(sys.argv) > 1:
        rc = RemoteConnector(launch_config.kernel_gate,
                             launch_config.gate_tunnel_user,
                             Curie(sys.argv[1]))
        print(rc.info)
    else:
        print('Need to provide curie [machine/key] on the command line.')


def _launch(launch_config, console_fun):
    """
    Launch with a given console function.
    :param launch_config: LaunchConfig.
    :param console_fun: console_fun(Launch instance) launches the console.
    :return:
    """
    if len(sys.argv) > 1:
        launch = Launch(launch_config.kernel_gate,
                        # 'in.chgate.net', 'chconnect',
                        launch_config.gate_tunnel_user,
                        sys.argv[1])
        console_fun(launch)
    else:
        print('Need to provide curie [machine/key] on the command line.')


def console(launch_config):
    """
    :param launch_config: LaunchConfig.
    """
    _launch(launch_config, start_console)


def qtconsole(launch_config):
    """
    :param launch_config: LaunchConfig.
    """
    _launch(launch_config, start_qtconsole)


def chconsole(launch_config):
    """
    :param launch_config: LaunchConfig.
    """
    _launch(launch_config, start_chconsole)
