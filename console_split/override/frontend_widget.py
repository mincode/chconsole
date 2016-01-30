from qtconsole.qt import QtCore

from console_split.ui.signaller import Signaller
from console_split.ui.signal_content import SignalContent, insert_signal_content, TextSignal

from console_split.modified_qtconsole.frontend_widget import FrontendWidget
_FrontendWidgetBase = FrontendWidget

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class FrontendWidget(_FrontendWidgetBase):
    stream_signaller = None

    #---------------------------------------------------------------------------
    # 'object' interface
    #---------------------------------------------------------------------------

    def __init__(self, *args, **kw):
        super(FrontendWidget, self).__init__(*args, **kw)
        self.stream_signaller = Signaller(self.ansi_codes)
        #Connect output slot
        self.stream_signaller.connect_signal(self.insert_stream_view)
        #print('init overridden FrontendWidget')

    @QtCore.Slot(SignalContent)
    def insert_stream_view(self, output):
        tabbed_output = type(output)(output.message.expandtabs(8))
        insert_signal_content(tabbed_output, self._view)

    #---------------------------------------------------------------------------
    # 'BaseFrontendMixin' abstract interface
    #---------------------------------------------------------------------------

    def _handle_stream(self, msg):
        """ Handle stdout, stderr, and stdin.
        """
        self.log.debug("stream: %s", msg.get('content', ''))
        if self.include_output(msg):
            self.flush_clearoutput()
            #self.append_stream(msg['content']['text'])
            to_append = msg['content']['text']
            self.stream_signaller.emit_signal(TextSignal(to_append))