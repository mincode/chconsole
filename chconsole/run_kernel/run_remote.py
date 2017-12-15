import time
import sys
from paramiko.client import SSHClient, AutoAddPolicy
import os
from chconsole.storage import JSONStorage, DefaultNames
import random
import string
# config file
from jupyter_core.paths import jupyter_config_dir
from chconsole import __version__
from traitlets.config.application import catch_config_error
from traitlets import Unicode
from jupyter_core.application import JupyterApp
# from jupyter_core.application import base_flags, base_aliases


__author__ = 'Manfred Minimair <manfred@minimair.org>'


_examples = """
jupyter chrun [session]                      # start a jupyter kernel with session.json connection file name
"""

# start with copy of base jupyter flags and aliases
# Aliases registered here are available from the command line, e.g.
# --username <Name>
# flags = dict(base_flags)
# aliases = dict(base_aliases)


class ChRunApp(JupyterApp, DefaultNames):
    name = 'jupyter-chrun'
    version = __version__
    description = """
        Run a remote Python kernel to be used by Chat Console.

        This launches a Python kernel on a remote server as configured
        in the configuration file of this application.

    """
    examples = _examples

    classes = []  # additional classes with configurable options
    # flags = Dict(flags)
    # aliases = Dict(aliases)

    kernel_host = Unicode('ses.chgate.net', config=True,
                          help='host to run kernel sessions')
    kernel_gate = Unicode('in.chgage.net', config=True,
                          help='gate ssh server that can see host and from which to start kernel sessions; gate and host must have idential user names and matching ssh keys to log in for starting the kernel')
    kernel_init_path = Unicode('', config=True,
                               help='path to kernel init file')
    kernel_init_file = Unicode('kernel_config.py', config=True,
                               help='file to run after kernel starts')
    gate_tunnel_user = Unicode('chconnect', config=True,
                               help='ssh user name on gate for tunnel to kernel')
    gate_tunnel_pem = Unicode(os.path.normcase(
        '/home/ec2-user/chrun_data/chconnect.pem'), config=True,
                       help='private ssh key for ssh user on gate for tunnel to kernel')
    gate_conn_dir = Unicode(os.path.normpath('/var/www/html'), config=True,
                            help='path of connection file on gate ssh server')
    host_conn_dir = Unicode('~', config=True,
                            help='path of connection file on kernel host')

    @catch_config_error
    def initialize(self, argv=None):
        super(ChRunApp, self).initialize(argv)
        if self._dispatching:
            return
        # more initialization code if needed

    def _run(self, ses_key=''):
        """
        Start a session remotely.
        :param ses_key: optional alpha-numeric session key;
        automatically generated if not present
        :return:
        """
        key_len = 8

        if ses_key:
            conn_key = ses_key
        else:
            conn_key = ''.join(random.choice(
                string.ascii_lowercase +
                string.digits) for _ in range(key_len))

        conn_file = conn_key + '.json'

        if self.kernel_init_path:
            kernel_startup = os.path.normcase(self.kernel_init_path + '/' +
                                              self.kernel_init_file)
        else:
            kernel_startup = self.kernel_init_file

        cmd = 'screen -dm ipython kernel' + \
              ' -f ' + self.host_conn_dir + '/' + conn_file + \
              '  --ip=0.0.0.0' + ' --user=' + DefaultNames.kernel_user + \
              ' --IPKernelApp.file_to_run=' + kernel_startup
        print(cmd)

        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(self.kernel_host)

        stdin, stdout, stderr = client.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        print('exit status: {}'.format(exit_status))
        for line in stdout.readlines():
            print(line.rstrip('\n'))

        if exit_status == 0:
            time.sleep(3)

            cmd = 'test -f ' + conn_file
            print(cmd)
            stdin, stdout, stderr = client.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()
            print('exit status: {}'.format(exit_status))
            for line in stdout.readlines():
                print(line.rstrip('\n'))

            if exit_status == 0:
                rem_file = conn_file
                loc_path = self.gate_conn_dir
                loc_file = os.path.normpath(os.path.join(
                    loc_path, conn_file))

                ftp = client.open_sftp()
                ftp.get(rem_file, loc_file)
                ftp.close()

                data = JSONStorage(loc_path, conn_file)
                data.set('ip', self.kernel_host)

                chat_tunnel = dict()
                chat_tunnel['gate'] = (self.gate_tunnel_user + '@' +
                                       self.kernel_gate)

                try:
                    with open(self.gate_tunnel_pem) as key_file:
                        print(self.gate_tunnel_pem + ' key file opened')
                        chat_tunnel['ssh_key'] = key_file.read()
                except FileNotFoundError:
                    chat_tunnel['ssh_key'] = ''

                data.set(DefaultNames.data_key, chat_tunnel)
                data.dump()

                if os.path.exists(loc_file):
                    print('[' + self.kernel_gate + '/' + conn_key + ']')
                else:
                    print('sftp of connection file failed!')
            else:
                print('Connection file is missing on session host!')
        else:
            print('Unable to start the kernel!')

    def start(self):
        super(ChRunApp, self).start()
        if len(sys.argv) > 1:
            self._run(sys.argv[1])
        else:
            self._run()


def _gen_default_config():
    """
    Generate the config file if it does not exist.
    :return: True if config file generated.
    """
    result = False
    config_location = os.path.join(jupyter_config_dir(),
                                   DefaultNames.chrun_config_file)
    if not os.path.exists(config_location):
        # cmd = ['jupyter-chrun', '--generate-config']
        # subprocess.run(cmd)
        config_flag = ChRunApp.generate_config
        ChRunApp.generate_config = True
        ChRunApp.launch_instance()
        ChRunApp.generate_config = config_flag
        result = True
    return result


def start_remote():
    if _gen_default_config():
        print('Ready to run application.')
    else:
        ChRunApp.launch_instance()


if __name__ == '__main__':
    start_remote()
