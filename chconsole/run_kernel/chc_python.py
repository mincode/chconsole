import sys, socket, re
from subprocess import Popen
from qtconsole.qt import QtGui
from chconsole.storage import JSONStorage, FileChooser, chconsole_data_dir, get_home_dir, DefaultNames

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class AppMain(QtGui.QMainWindow, DefaultNames):
    storage = None  # JSONStorage
    chooser = None  # FileChooser
    text_area = None  # QPlainTextEdit, output text area

    def __init__(self):
        super(AppMain, self).__init__()

        self.storage = JSONStorage(chconsole_data_dir(), self.default_file)
        self.chooser = FileChooser(self.storage, self.storage_key, get_home_dir(), self.default_file,
                                   parent=None, caption='Choose Connection File', file_filter='*.json',
                                   default_ext='json')

        self.text_area = QtGui.QPlainTextEdit()
        self.text_area.setReadOnly(True)
        self.setCentralWidget(self.text_area)

        self.setGeometry(300, 300, 500, 200)
        self.setWindowTitle('Python Kernel Launched')

    def launch(self, app):
        if self.chooser.choose_file():
            Popen(['ipython', 'kernel', '-f', self.chooser.file])
            self.text_area.insertPlainText('Local connection file:\n')
            self.text_area.insertPlainText('    ' + self.chooser.file + '\n')

            local_connect = JSONStorage(self.chooser.dir, self.chooser.name)
            lan_name = re.sub(r"\.json$", '-lan.json', self.chooser.name)
            lan_connect = JSONStorage(self.chooser.dir, lan_name)
            lan_connect.data = local_connect.data.copy()
            hostname = socket.gethostname()
            lan_connect.set('hostname', hostname)
            ip = socket.gethostbyname(hostname)
            lan_connect.set('ip', ip)

            self.text_area.insertPlainText('\nThis window may be closed. The kernel will keep running!')
            self.show()
        else:
            sys.exit(app.quit())


def main():
    app = QtGui.QApplication(sys.argv)
    app_main = AppMain()
    app_main.launch(app)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
