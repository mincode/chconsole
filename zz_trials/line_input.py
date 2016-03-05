import sys

from qtconsole.qt import QtGui

from ui.entry.line_prompt import LinePrompt

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class Outer(QtGui.QFrame):
    line = None

    def __init__(self):
        super().__init__()

    # def showEvent(self, event):
    #     if not event.spontaneous():
    #         print('line.width: ' + str(self.line.width()))
    #         horizontal = max(0, self.width()-self.line.width())
    #         vertical = max(0, self.height()-self.line.height())
    #         self.line.move(horizontal/2, vertical/2)

def main():

    app = QtGui.QApplication(sys.argv)

    outer = Outer()
    outer.resize(500, 300)
    w = LinePrompt()
    outer.line = w
    w.setParent(outer)
    w.prompt = 'Enter: '
    print('w.width: ' + str(w.width()))
    geometry = outer.geometry()
    print('outer.width: ' + str(outer.width()))
    w.show()
    outer.setWindowTitle('Simple')
    outer.show()
    print('w.width: ' + str(w.width()))

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
