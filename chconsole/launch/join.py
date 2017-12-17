import os
import enum
from chconsole.launch.launch_config import LaunchConfig
from chconsole.storage import DefaultNames
from jupyter_core.paths import jupyter_config_dir
from chconsole import __version__
from traitlets.config.application import catch_config_error
from traitlets import Dict, CBool, UseEnum, Unicode
from jupyter_core.application import JupyterApp, base_flags, base_aliases
from traitlets.config.application import boolean_flag
from chconsole.launch import Launch, start_chconsole, start_console, start_qtconsole

__author__ = 'Manfred Minimair <manfred@minimair.org>'


_examples = """
jupyter chjoin                      # start a chconsole connected to a remote session
"""

flags = dict(base_flags)
# Flags from boolean_flog allow uses such
# as --force-username, --no-force-username
flags.update(boolean_flag(
    'gui', 'JoinApp.gui',
    "Use gui to connect to launch console."
))
flags.update(boolean_flag(
    'force-username', 'JoinApp.require_username',
    "Require entering a user name in the gui."
    "Use the pre-determined user name if none given."
))

aliases = dict(base_aliases)
new_aliases = dict(
    keye='JoinApp.key'
)
aliases.update(new_aliases)


class ConsoleType(enum.Enum):
    chat = 1
    qt = 2
    text = 3


class JoinApp(JupyterApp):

    name = 'jupyter-chjoin'
    version = __version__
    description = """
        Launch Chat Console connected to a remote kernel.

        This launches a chconsole instance locally connected
        to a Python kernel running remotely.

    """
    examples = _examples

    classes = [LaunchConfig]  # additional classes with configurable options
    flags = Dict(flags)
    aliases = Dict(aliases)

    gui = CBool(True, config=True,
                help="Whether to launch through gui; only launches chat console through gui")

    require_username = CBool(True, config=True,
                             help="Whether to require input of username\
                             in gui")

    console_type = UseEnum(ConsoleType, default_value=ConsoleType.chat)

    key = Unicode('', config=True, help='Session identifier to connect to.')

    launch_config = None  # LaunchConfig

    @catch_config_error
    def initialize(self, argv=None):
        super(JoinApp, self).initialize(argv)
        if self._dispatching:
            return
        # more initialization code if needed
        self.launch_config = LaunchConfig()

    def start(self):
        super(JoinApp, self).start()
        if self.gui:
            print('gui: {}'.format(self.gui))
        else:
            launch = Launch(self.launch_config.kernel_gate,
                            self.launch_config.gate_tunnel_user,
                            self.key)
            if self.console_type == ConsoleType.chat:
                start_chconsole(launch)

            elif self.console_type == ConsoleType.qt:
                start_qtconsole(launch)

            else:  # self.console_type == ConsoleType.text:
                start_console(launch)


def _gen_default_config():
    """
    Generate the config file if it does not exist.
    :return: True if config file generated.
    """
    gen_config = False
    config_location = os.path.join(jupyter_config_dir(),
                                   DefaultNames.chjoin_config_file)
    if not os.path.exists(config_location):
        gen_config = True
        JoinApp.config_file = config_location
        JoinApp.generate_config = gen_config
        JoinApp.launch_instance()

    return gen_config


def main():
    if _gen_default_config():
        print('Ready to run application.')
    else:
        JoinApp.launch_instance()


if __name__ == '__main__':
    main()
