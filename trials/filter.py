__author__ = 'Manfred Minimair <manfred@minimair.org>'

import sys
from qtconsole.qt import QtGui, QtCore


class KeyFilter(QtCore.QObject):
    def __init__(self):
        super().__init__()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            print('filter super: '+str(key))
            return False
        else:
            return False

class SubFilter(QtCore.QObject):
    def __init__(self):
        super().__init__()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            print('filter sub: '+str(key))
            return False
        else:
            return False


class MainWidget(QtGui.QTextEdit):
    def __init__(self):
        super().__init__()
        self.key_filter = KeyFilter()
        self.installEventFilter(self.key_filter)

    # def event(self, event):
    #     if event.type() == QtCore.QEvent.KeyPress:
    #         key = event.key()
    #         if key==75:
    #             print('event super: '+str(key))
    #             return True
    #         else:
    #             return super(MainWidget, self).event(event)
    #             #return False
    #     else:
    #         return False

class SubMain(MainWidget):
    def __init__(self):
        super().__init__()
        self.sub_filter = SubFilter()
        self.installEventFilter(self.sub_filter)

    # def event(self, event):
    #     if event.type() == QtCore.QEvent.KeyPress:
    #         key = event.key()
    #         if key==74:
    #             print('event sub: '+str(key))
    #             return True
    #         else:
    #             return super(SubMain,self).event(event)
    #     else:
    #         return False

def main():
    app = QtGui.QApplication(sys.argv)
    w = SubMain()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
