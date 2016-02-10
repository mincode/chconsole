import sys
from qtconsole.qt import QtGui

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class MainWidget(QtGui.QTextEdit):
    def __init__(self):
        super().__init__()
        doc = self.document()
        print('block count before insert first: {0}'.format(doc.blockCount()))
        cursor = self.textCursor()
        cursor.insertText('first block!')
        print('block count after insert first: {0}'.format(doc.blockCount()))

        cursor.movePosition(QtGui.QTextCursor.PreviousCharacter)
        cursor.insertBlock()
        print('block count after insert block: {0}'.format(doc.blockCount()))

        it = doc.rootFrame().begin()
        while it != doc.rootFrame().end():
            print('-- iterate over root')
            print(it.currentFrame())
            print(it.currentBlock().isValid())
            if it.currentBlock().isValid():
                print('-----------text: ' + it.currentBlock().text())
            it += 1


        # frame = cursor.insertFrame(QtGui.QTextFrameFormat())
        # # print(frame)
        # print('block count after frame: {0}'.format(doc.blockCount()))
        # cursor.insertText('second block')
        # cursor.insertText(' more second')
        # cursor.insertText('\nthird block')
        #
        # # block0 = doc.findBlockByNumber(0)
        # # block0 = doc.findBlockByLineNumber(0)
        # # cursor0 = QtGui.QTextCursor(block0)
        # # cursor0.select(QtGui.QTextCursor.BlockUnderCursor)
        # # cursor0.removeSelectedText()
        # # cursor0.deleteChar()
        # print('block count after second: {0}'.format(doc.blockCount()))
        #
        # end = doc.lastBlock()
        # end_cursor = QtGui.QTextCursor(end)
        # end_cursor.insertText('end block')
        # print('block count after end: {0}'.format(doc.blockCount()))
        #
        #
        # # print('cursor position: {0}'.format(cursor.position()))
        # # start = cursor.position()
        #
        # # frames = doc.rootFrame().childFrames()
        # # print(frames)
        #
        # it = frame.begin()
        # while it != frame.end():
        #     print('++ iterate over frame')
        #     print(it.currentBlock().text())
        #     it += 1
        #
        # it = doc.rootFrame().begin()
        # while it != doc.rootFrame().end():
        #     print('-- iterate over root')
        #     print(it.currentFrame())
        #     print(it.currentBlock().isValid())
        #     if it.currentBlock().isValid():
        #         print('-----------text: ' + it.currentBlock().text())
        #     it += 1
        #     # if it.atEnd():
        #     #     break

        # print('cursor position: {0}'.format(cursor.position()))
        # cursor.select(QtGui.QTextCursor.BlockUnderCursor)

        # block = doc.begin()
        # count = 0
        # print()
        # while block != doc.end():
        #     print('block: ' + str(count))
        #     print(block.text())
        #     block = block.next()
        #     count += 1


def main():
    app = QtGui.QApplication(sys.argv)
    w = MainWidget()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
