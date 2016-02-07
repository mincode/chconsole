__author__ = 'Manfred Minimair <manfred@minimair.org>'

# QComboBox *comboBox = new QComboBox(menu);
# QWidgetAction *checkableAction = new QWidgetAction(menu);
# checkableAction->setDefaultWidget(comboBox);
# menu->addAction(checkableAction);


def entry_template(edit_class):
    """
    Template for Entry.
    :param edit_class: QTGui.QTextEdit or QtGui.QPlainTextEdit
    :return: Instantiated class.
    """
    class Entry:
        pass

    return Entry
