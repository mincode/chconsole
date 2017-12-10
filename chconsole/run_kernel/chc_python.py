import sys
import socket
import os
import time
import getpass
from subprocess import Popen
from qtconsole.qt import QtGui
from chconsole.storage import JSONStorage, FileChooser, chconsole_data_dir, get_home_dir, DefaultNames

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class AppMain(QtGui.QMainWindow, DefaultNames):
    max_ipython_start_time = 5
    # maximum number of seconds allowed for ipython to create a connection file,
    # if it does not exist
    sleep_time = 0.1  # time to repeatedly wait until connection file has been created by the kernel.
    storage = None  # JSONStorage
    chooser = None  # FileChooser
    text_area = None  # QPlainTextEdit, output text area

    default_user_name = ''  # default user name to be used for the kernel

    def __init__(self):
        super(AppMain, self).__init__()

        self.storage = JSONStorage(chconsole_data_dir(), self.default_file)
        self.chooser = FileChooser(self.storage, self.storage_key, get_home_dir(), self.default_file,
                                   parent=None, caption='Choose Connection File or Enter New File Name',
                                   file_filter='*.json',
                                   default_ext='json')

        self.text_area = QtGui.QPlainTextEdit()
        self.text_area.setReadOnly(True)
        self.setCentralWidget(self.text_area)

        self.setGeometry(300, 300, 700, 200)
        self.setWindowTitle('IPython Kernel Launched')

    @property
    def _user_name(self):
        """
        Get the user name to the application. Either self.user_name if it is not '' or None,
        or kernel-USER environment variable if it is assigned, or kernel-getpass.getuser(), or 'kernel-user'
        if getpass.getuser() fails.
        :return: user name
        """
        prefix = 'kernel_'
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

    def launch(self, app):
        if self.chooser.choose_file():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('8.8.8.8', 1))  # connecting to a UDP address doesn't send packets
                local_ip_address = s.getsockname()[0]
            except (socket.timeout, InterruptedError):
                local_ip_address = socket.gethostbyname(socket.getfqdn())

            cmd = ['ipython', 'kernel', '-f', self.chooser.file,
                   '--ip', local_ip_address, '--user', self._user_name]

            Popen(cmd)

            # Ensure the connection file has been created
            wait_time = 0
            while wait_time < self.max_ipython_start_time and not os.path.exists(self.chooser.file):
                time.sleep(self.sleep_time)
                wait_time += self.sleep_time
            if not os.path.exists(self.chooser.file):
                print('Error: Kernel did not create the chosen connection file:')
                print(self.chooser.file)
                sys.exit(app.exit(1))

            self.text_area.insertPlainText('Connection file for Chat Console:\n')
            self.text_area.insertPlainText(self.chooser.file + '\n')

            self.text_area.insertPlainText('\nCommand used to start IPython:\n')
            self.text_area.insertPlainText(' '.join(cmd) + '\n')

            self.text_area.insertPlainText('\nThis window may be closed. The kernel will keep running!\n')
            self.text_area.insertPlainText('The kernel can be stopped by connecting a console '
                                           'and entering the quit command.')
            self.show()
        else:
            sys.exit(app.quit())


def start_local():
    app = QtGui.QApplication(sys.argv)
    app_main = AppMain()
    app_main.launch(app)
    sys.exit(app.exec_())


if __name__ == '__main__':
    start_local()
