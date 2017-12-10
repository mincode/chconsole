import time
import sys
from paramiko.client import SSHClient, AutoAddPolicy
import os
from chconsole.storage import JSONStorage, DefaultNames
import random
import string


__author__ = 'Manfred Minimair <manfred@minimair.org>'


def _run(ses_key=''):
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
            string.ascii_lowercase + string.digits) for _ in range(key_len))

    conn_file = conn_key + '.json'

    cmd = 'screen -dm ipython kernel' + \
          ' -f ' + DefaultNames.remote_conn_dir + '/' + conn_file + \
          '  --ip=0.0.0.0' + ' --user ' + DefaultNames.kernel_user
    print(cmd)

    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(DefaultNames.host)

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
            loc_path = DefaultNames.local_conn_dir
            loc_file = os.path.normpath(os.path.join(loc_path, conn_file))

            ftp = client.open_sftp()
            ftp.get(rem_file, loc_file)
            ftp.close()

            data = JSONStorage(loc_path, conn_file)
            data.set('ip', DefaultNames.host)

            chat_tunnel = dict()
            chat_tunnel['gate'] = (DefaultNames.gate_user + '@' +
                                   DefaultNames.gate)

            try:
                with open(DefaultNames.gate_pem) as key_file:
                    print(DefaultNames.gate_pem + ' key file opened')
                    chat_tunnel['ssh_key'] = key_file.read()
            except FileNotFoundError:
                chat_tunnel['ssh_key'] = ''

            data.set(DefaultNames.data_key, chat_tunnel)
            data.dump()

            if os.path.exists(loc_file):
                print('[' + DefaultNames.gate + '/' + conn_key + ']')
            else:
                print('sftp of connection file failed!')
        else:
            print('Connection file is missing on session host!')
    else:
        print('Unable to start the kernel!')


def start_remote():
    if len(sys.argv) > 1:
        _run(sys.argv[1])
    else:
        _run()


if __name__ == '__main__':
    start_remote()
