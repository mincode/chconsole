import sys
from qtconsole.qt import QtGui
from chconsole.launch import start_chconsole, Launch
from chconsole.connect import Curie
# config file
import os
from chconsole.launch.launch_config import LaunchConfig
from chconsole.storage import DefaultNames
from jupyter_core.paths import jupyter_config_dir
from chconsole import __version__
from traitlets.config.application import catch_config_error
from traitlets import Dict, CBool
from jupyter_core.application import JupyterApp, base_flags
from traitlets.config.application import boolean_flag
# from qtconsole.util import MetaQObjectHasTraits


__author__ = 'Manfred Minimair <manfred@minimair.org>'


_examples = """
jupyter chgui_launch [session]                      # start a chconsole connected to a remote session
"""

flags = dict(base_flags)
# Flags from boolean_flog allow uses such
# as --force-username, --no-force-username
flags.update(boolean_flag(
    'force-username', 'ChGuiLaunchApp.require_username',
    "Require entering a user name in the gui."
    "Use the pre-determined user name if none given."
))


# class LaunchWidget(MetaQObjectHasTraits('NewBase',
#                                         (LoggingConfigurable, QtGui.QWidget), {})):
class LaunchWidget(QtGui.QWidget):

    def __init__(self, kernel_gate, gate_tunnel_user,
                 request_user_name=True, parent=None):
        """
        Initialize.
        :param kernel_gate: url of kernel gate.
        :param gate_tunnel_user: user name to tunnel through gate to kernel.
        :param request_user_name:
               whether user should enter a user name for chat.
        """
        super(LaunchWidget, self).__init__(parent)

        self.kernel_gate = kernel_gate
        self.gate_tunnel_user = gate_tunnel_user
        self.request_user_name = request_user_name
        self.setWindowTitle('Chat Console')
        self.notify = QtGui.QLabel('Connect with Chat Console' + ' ' * 60)
        self.input_user = _UserNameEntry()
        self.input_curie = _CurieEntry()
        self.button = QtGui.QPushButton('Submit')
        self.button.clicked.connect(self.finished)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.notify)
        layout.addWidget(self.input_user)
        layout.addWidget(self.input_curie)
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.show()

    def finished(self):
        if self.request_user_name and not self.input_user.text():
            msg = QtGui.QMessageBox(self)
            msg.setWindowTitle('Chat Console')
            msg.setText('Please enter your chat user name.')
            msg.setStandardButtons(QtGui.QMessageBox.Ok)
            msg.show()
        else:
            user_name = self.input_user.text().strip()
            curie = self.kernel_gate + '/' + self.input_curie.text().strip()
            if Curie.valid(curie):
                try:
                    launch = Launch(self.kernel_gate,
                                    self.gate_tunnel_user,
                                    curie, user_name)
                    start_chconsole(launch)
                except Exception:
                    msg = QtGui.QMessageBox(self)
                    msg.setWindowTitle('Chat Console')
                    msg.setText('Remote connection cannot be established.')
                    msg.setStandardButtons(QtGui.QMessageBox.Ok)
                    msg.show()
            else:
                msg = QtGui.QMessageBox(self)
                msg.setWindowTitle('Chat Console')
                msg.setText('Invalid launch information.')
                msg.setStandardButtons(QtGui.QMessageBox.Ok)
                msg.show()


class _CurieEntry(QtGui.QLineEdit):
    def __init__(self):
        super(_CurieEntry, self).__init__()

        self.setPlaceholderText('Enter launch information')


class _UserNameEntry(QtGui.QLineEdit):
    def __init__(self):
        super(_UserNameEntry, self).__init__()

        self.setPlaceholderText('Enter chat user name')


class ChGuiLaunchApp(JupyterApp):

    name = 'jupyter-chgui_launch'
    version = __version__
    description = """
        Launch Chat Console connected to a remote kernel.

        This launches a chconsole instance locally connected
        to a Python kernel running remotely.

    """
    examples = _examples

    classes = [LaunchConfig]  # additional classes with configurable options
    flags = Dict(flags)

    require_username = CBool(True, config=True,
                             help="Whether to require input of username")

    launch_config = None  # LaunchConfig

    @catch_config_error
    def initialize(self, argv=None):
        super(ChGuiLaunchApp, self).initialize(argv)
        if self._dispatching:
            return
        # more initialization code if needed
        self.launch_config = LaunchConfig()

    def start(self):
        super(ChGuiLaunchApp, self).start()
        self.widget = LaunchWidget(self.launch_config.kernel_gate,
                                   self.launch_config.gate_tunnel_user,
                                   self.require_username)
        self.widget.show()


def _gen_default_config():
    """
    Generate the config file if it does not exist.
    :return: True if config file generated.
    """
    result = False
    config_location = os.path.join(jupyter_config_dir(),
                                   DefaultNames.chgui_launch_config_file)
    if not os.path.exists(config_location):
        # cmd = ['jupyter-chgui_launch', '--generate-config']
        # subprocess.run(cmd)
        config_flag = ChGuiLaunchApp.generate_config
        ChGuiLaunchApp.generate_config = True
        ChGuiLaunchApp.launch_instance()
        ChGuiLaunchApp.generate_config = config_flag
        result = True
    return result


def gui_chconsole():
    if _gen_default_config():
        print('Ready to run application.')
    else:
        app = QtGui.QApplication(sys.argv)
        ChGuiLaunchApp.launch_instance()
        sys.exit(app.exec_())


if __name__ == '__main__':
    gui_chconsole()
