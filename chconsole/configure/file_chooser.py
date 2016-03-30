import os, re
from qtconsole.qt import QtGui
from .persistent import Persistent

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class FileChooser(QtGui.QFileDialog):
    _default_dir = ''  # default directory
    _dir = None  # Persistent directory
    _default_name = ''  # default file name
    _name = None  # Persistent file name
    _default_ext = ''  # default filename extension enforced if the user enters a new file name without extension

    def __init__(self, storage, key_id='', default_dir='', default_name='',
                 parent=None, caption='', file_filter='', default_ext=''):
        super(FileChooser, self).__init__(parent, caption)
        self.setFilter(file_filter)
        self.setFileMode(QtGui.QFileDialog.AnyFile)

        name_key = key_id + ': file'
        dir_key = key_id + ': dir'

        self._default_dir = default_dir
        self._default_name = default_name
        self._dir = Persistent(storage, dir_key, self._default_dir)
        self._name = Persistent(storage, name_key, self._default_name)

        self.setDirectory(self._dir.get())
        self.selectFile(self._name.get())
        self._default_ext = default_ext

    def choose_file(self):
        """
        Show file chooser dialog
        :return: QDioalog.Accpeted != 0 or QDialog.Rejected == 0
        """
        accepted = self.exec_()
        if accepted:
            file_names = self.selectedFiles()
            print(file_names)
            file = file_names[0]
            path, base = os.path.split(file)
            if re.match(r".*\."+self._default_ext+r"$", base) is None:
                base += '.json'
            self._dir.set(path)
            self._name.set(base)
        return accepted

    @property
    def dir(self):
        """
        Chosen directory
        :return: chosen directory
        """
        return self._dir.get()

    @property
    def name(self):
        """
        Chosen file name
        :return: chosen file name
        """
        return self._name.get()
