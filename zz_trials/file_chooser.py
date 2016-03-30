
import sys, os, re
from PyQt4 import QtGui
from chconsole.configure import Storage
from chconsole.configure import Persistent


class FileChooser(QtGui.QFileDialog):
    _storage = None  # Storage
    _id = ''  # unique object identifyer used for storing file names and paths
    _default_dir = ''  # default directory
    _dir = None  # Persistent directory
    _dir_key = ''  # identifier for _dir in the storage
    _default_name = ''  # default file name
    _name = None  # Persistent file name
    _name_key = ''  # identifier for _name in the storage
    _default_ext = ''  # default filename extension enforced if the user enters a new file name without extension

    def __init__(self, storage, key_id='', default_dir='', default_name='',
                 parent=None, caption='', file_filter='', default_ext=''):
        super(FileChooser, self).__init__(parent, caption)
        self.setFilter(file_filter)
        self.setFileMode(QtGui.QFileDialog.AnyFile)

        self._id = key_id
        self._name_key = self._id + ': file'
        self._dir_key = self._id + ': dir'

        self._storage = storage
        self._default_dir = default_dir
        self._default_name = default_name
        self._dir = Persistent(self._storage, self._dir_key, self._default_dir)
        self._name = Persistent(self._storage, self._name_key, self._default_name)

        self.setDirectory(self._dir.get())
        self.selectFile(self._name.get())
        self._default_ext = default_ext

    def show_dialog(self):
        # self.chooser.show()

        if self.exec_():
            file_names = self.selectedFiles()
            print(file_names)
            file = file_names[0]
            path, base = os.path.split(file)
            if re.match(r".*\."+self._default_ext+r"$", base) is None:
                base += '.json'
            self._storage.set(self._dir_key, path)
            self._storage.set(self._name_key, base)
            print('path: ' + path)
            print('file: ' + base)
            # fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
            #         '/home')
            #
            # f = open(fname, 'r')
            #
            # with f:
            #     data = f.read()
            #     self.textEdit.setText(data)


class Example(QtGui.QMainWindow):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        self.storage = Storage('K:\\UserData\\minimair\\Documents', 'the-config.json')
        self.chooser = FileChooser(self.storage, 'key0', 'K:\\UserData\\minimair\\Documents', 'the-file.json',
                                   parent=None, caption='Choose Connection File', file_filter='*.json',
                                   default_ext='json')

        self.textEdit = QtGui.QTextEdit()
        self.setCentralWidget(self.textEdit)
        self.statusBar()

        openFile = QtGui.QAction(QtGui.QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.chooser.show_dialog)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)       
        
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('File dialog')
        self.show()
        

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
