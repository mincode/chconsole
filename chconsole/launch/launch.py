import os
import getpass
import subprocess
from jupyter_core.paths import jupyter_config_dir
from chconsole.connect import RemoteConnector, Curie
from chconsole.storage import DefaultNames

__author__ = 'Manfred Minimair <manfred@minimair.org>'


def start_console(launch):
    """
    :param launch: Launnch
    Start the Jupyter console.
    :return:
    """
    launch.start('jupyter-console', '--ZMQTerminalIPythonApp.sshkey=')


def start_qtconsole(launch):
    """
    Start the Jupyter qtconsole.
    :param launch: Launnch
    :return:
    """
    launch.start('jupyter-qtconsole', '--JupyterQtConsoleApp.sshkey=')


def _gen_chconsole_config():
    """
    Generate the chconsole config file if it does not exist.
    :return:
    """
    config_location = os.path.join(jupyter_config_dir(),
                                   DefaultNames.config_file)
    if not os.path.exists(config_location):
        cmd = ['jupyter-chconsole', '--generate-config']
        subprocess.run(cmd)


def start_chconsole(launch):
    """
    :param launch: Launnch
    Start the Jupyter qtconsole.
    :return:
    """
    _gen_chconsole_config()
    launch.start('jupyter-chconsole', '--ChatConsoleApp.sshkey=',
                 ['--JupyterQtConsoleApp.answer_yes=True'])


class Launch:
    """
    Launchers for Jupyter console-type applications.
    """

    default_user_name = None  # string; 
    # default user name to be used for the application

    remote = None  # RemoteConnector

    def __init__(self, curie, user_name=''):
        """
        Init.
        :param curie: curie string for remote connection.
        :param user_name: user name to be used for the application.
        """
        self.remote = RemoteConnector(Curie(curie))
        self.default_user_name = user_name

    @property
    def _user_name(self):
        """
        Get the user name to the application.
        Either self.user_name if it is not '' or None,
        or ch_USER environment variable if it is assigned,
        or 'ch_'+getpass.getuser(),
        or 'ch_user' if getpass.getuser() fails.
        :return: user name
        """
        prefix = 'ch_'
        user_name = self.default_user_name
        if not user_name:
            user_name = os.getenv('USER', default=None)
            if user_name is None:
                try:
                    user_name = getpass.getuser()
                except Exception:
                    user_name = 'user'
                user_name = prefix + user_name
        return user_name

    def start(self, what='jupyter-console',
              sshkey_param='--ZMQTerminalIPythonApp.sshkey=', other=[]):
        """
        Run application.
        :param what: application to run.
        :param sshkey_param: string for parameter to assign the
        ssh key location; used as sshkey_param+sshkey
        :param other: list of strings of other options to pass to console
        :return:
        """
        cmd = [what, sshkey_param+self.remote.abs_key_file,
               '--ssh='+self.remote.ssh_target,
               '--existing='+self.remote.abs_conn_file,
               '--user='+self._user_name]
        # '--Session.username='+self._user_name]
        # This username option does not work in Windows.
        # Therefore use the newly defined options
        # '--user', or equivalently
        # '--username'
        cmd.extend(other)
        # print(cmd)
        subprocess.run(cmd)
