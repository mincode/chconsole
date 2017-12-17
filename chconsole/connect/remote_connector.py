import requests
import os
import stat
from chconsole.storage import chconsole_data_dir, JSONStorage, DefaultNames
from chconsole.standards import NoRemoteConnection, ChangeModFailed


__author__ = 'Manfred Minimair <manfred@minimair.org>'


def _write_ssh_key(path, key_file, key):
    """
    Write ssh key file.
    :param path:
    :param key_file:
    :param key:
    :return:
    """
    pem_file = os.path.normpath(os.path.join(path, key_file))
    with open(pem_file, 'w') as f:
        f.write(key)
    if os.path.exists(pem_file):
        try:
            os.chmod(pem_file, stat.S_IRUSR | stat.S_IWUSR)
        except os.error:
            raise ChangeModFailed(pem_file)


def _write_conn_info(path, conn_file, info):
    """
    Write a connection file.
    :param path: destination path for the connection file.
    :param conn_file: name of the connection file
    :param info: json data for the connection file.
    :return:
    """
    store = JSONStorage(path, conn_file)
    store.data = info
    store.dump()


class RemoteConnector:
    """
    Configuration information needed to connect to a remote session
    via ssh tunnels.
    """
    _machine = ''  # machine name to ssh into
    _key = ''  # session key for connection file
    _response = None  # requests.Response for the connection

    info = None  # dict with json of the remote connection file

    def __init__(self, kernel_gate, gate_tunnel_user, curie, **kw):
        """
        Init.
        :param kernel_gate: ip of gate to kernel
        :param gate_tunnel_user: user name for tunneling to kernel through gate
        :param: curie: specifying the remote connection
        """
        self.kernel_gate = kernel_gate
        self.gate_tunnel_user = gate_tunnel_user

        self._machine = curie.machine
        self._key = curie.key

        self._response = requests.get(self.remote_file_url, verify=False)
        if self._response.status_code == 200:
            self.info = self._response.json()
        else:
            raise NoRemoteConnection(self._response,
                                     self._response.status_code)

        if self.storage_dir:
            os.makedirs(self.storage_dir, exist_ok=True)

        _write_ssh_key(self.storage_dir, self.key_file,
                       self.info[DefaultNames.data_key]['ssh_key'])
        self.info.pop(DefaultNames.data_key, None)
        _write_conn_info(self.storage_dir, self.conn_file, self.info)

    @property
    def remote_file_url(self):
        """
        Remote connection file to access.
        :return: url of remote connection file to access.
        """
        return 'https://' + self._machine + '/' + self.conn_file

    @property
    def storage_dir(self):
        """
        Local storage directory.
        :return: name of local storage directory as a string.
        """
        return chconsole_data_dir()

    @property
    def key_file(self):
        """
        SSH key file.
        :return: name of ssh key file.
        """
        return self._key + '.pem'

    @property
    def abs_key_file(self):
        """
        SSH key file with absolute path.
        :return: name of ssh key file with absolute path.
        """
        return os.path.join(self.storage_dir, self.key_file)

    @property
    def ssh_target(self):
        """
        SSH user@machine
        :return: string with user@machine.
        """
        return self.gate_tunnel_user + '@' + self.kernel_gate

    @property
    def conn_file(self):
        """
        Connection file.
        :return: name of connection file.
        """
        return self._key + '.json'

    @property
    def abs_conn_file(self):
        """
        Connection file with absolute path.
        :return: name of connection file with absolute path
        """
        return os.path.join(self.storage_dir, self.conn_file)
