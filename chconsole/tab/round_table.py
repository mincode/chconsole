from traitlets import Integer, Unicode
from traitlets.config.configurable import LoggingConfigurable
from qtconsole.util import MetaQObjectHasTraits
from qtconsole.qt import QtCore, QtGui
from chconsole.messages import Stdout, StartRoundTable, StopRoundTable, ExportItem, ImportItem

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class RoundTable(MetaQObjectHasTraits('NewBase', (LoggingConfigurable, QtCore.QObject), {})):
    """
    Information to organize a round table of users with restrictions on the number of inputs.
    """
    chat_secret = ''  # secret for chat communication
    client_id = ''  # id of current client
    user_name = ''  # name of current user
    update_view = QtCore.Signal()  # tasks for the main window process to update the view of the round table
    please_export = QtCore.Signal(ExportItem)  # tasks for the kernel
    please_process = QtCore.Signal(ImportItem)  # internal tasks

    default_restriction = Integer(3, config=True,
                                              help="""
            Number of posts per user per round table. Negative number means no restriction.
            """)
    restriction = default_restriction  # negative number means no restriction

    moderator = Unicode('', help='Name of the round table moderator')

    def __init__(self, chat_secret, client_id, user_name, parent=None, **kwargs):
        """
        Initialize.
        :param chat_secret: secret for chat communication.
        :param client_id: id of current user client.
        :param user_name: name of current user.
        :param parent: parent QObject; default None.
        """
        QtCore.QObject.__init__(self, parent)
        LoggingConfigurable.__init__(self, **kwargs)

        self.chat_secret = chat_secret
        self.client_id = client_id
        self.user_name = user_name

    @property
    def user_is_moderator(self):
        """
        Determine whether the current user is the round table moderator.
        :return: True iff the current user is the round table moderator.
        """
        return self.moderator == self.user_name

    @property
    def no_moderator(self):
        """
        Determine whether there is no round table moderator registered.
        :return: True if there is no round table moderator.
        """
        return self.moderator == ''

    def _moderator_changed(self):
            # print('moderator changed to: ' + self.round_table_moderator)
            self.update_view.emit()
            # connected to update_round_table_checkbox

    def update_moderator(self, other_round_table, other_moderator, other_restriction):
        """
        Update the moderator and notify locally if the other has a round table and
        the current user is not the moderator.
        :param other_round_table: True if the other has a round table.
        :param other_moderator: name of the other moderator.
        :param other_restriction: input restriction of the other round table.
        :return:
        """
        if other_round_table and self.no_moderator:
            self.moderator = other_moderator
            self.restriction = other_restriction
            self.please_process.emit(Stdout('\nRound table run by ' + self.moderator))

    def set_moderator(self, moderator=''):
        """
        Set the round table moderator and notify connected users if the current user becomes or
        ceases to be the moderator.
        :param moderator: user name of moderator.
        :return:
        """
        self.moderator = moderator
        if moderator == self.user_name:
            self.please_export.emit(StartRoundTable(self.chat_secret, self.client_id, self.user_name,
                                                    restriction=self.restriction))
            # self.post(Stdout('\nRound table started by ' + self.round_table_moderator))
        elif moderator == '':
            self.please_export.emit(StopRoundTable(self.chat_secret, self.client_id, self.user_name))
            self.please_process.emit(Stdout('\nRound table stopped by ' + self.user_name))
            # otherwise do not send anything

    def allow_input(self):
        """
        Determine if round table allows another input; counts down the restriction count and emits an
        update view signal for the main window.
        :return: True if round table allows another input.
        """
        allow_input = True
        # print('restr: {0}'.format(self.restriction))
        if not self.user_is_moderator and self.moderator:
            if self.restriction == 0:
                warning = QtGui.QMessageBox(self.parent)
                warning.setIcon(QtGui.QMessageBox.Information)
                warning.setText('No more inputs allowed!')
                warning.setWindowTitle('Round Table')
                warning.setStandardButtons(QtGui.QMessageBox.Ok)
                warning.exec_()
                allow_input = False
            elif self.restriction > 0:
                self.restriction = self.restriction - 1
                # notify menu that it changed
                self.update_view.emit()
        return allow_input

    def stop(self, other):
        """
        Stop the other's round table and notify locally.
        :param other: name of the other moderator.
        :return:
        """
        if other == self.moderator:
            self.moderator = ''
            self.restriction = self.default_restriction
            self.please_process.emit(Stdout('\nRound table stopped by ' + other))

    def stop_on_exit(self, other_round_table, other, other_last_client):
        """
        Stop the round table if the other is the last client of the moderator
        and notify locally.
        :param other_round_table: True if the other moderates the round table.
        :param other: name of the other moderator.
        :param other_last_client: True if the other's client is the last one.
        :return:
        """
        if other_round_table and other_last_client:
            self.stop(other)

    def start(self, other, other_restriction):
        """
        Start round table and notify locally.
        :param other: name of other moderator for the round table.
        :param other_restriction: input restriction by other moderator.
        :return:
        """
        self.moderator = other
        self.please_process.emit(Stdout('\nRound table started by ' + self.moderator))
        if self.moderator == self.user_name:
            self.restriction = self.default_restriction
        else:
            self.restriction = other_restriction
