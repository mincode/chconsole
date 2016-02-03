from console_split.ui.signal_content import TextSignal

from console_split.modified_qtconsole.frontend_widget import FrontendWidget
_FrontendWidgetBase = FrontendWidget

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class FrontendWidget(_FrontendWidgetBase):
    #---------------------------------------------------------------------------
    # 'object' interface
    #---------------------------------------------------------------------------

    def __init__(self, *args, **kw):
        super(FrontendWidget, self).__init__(*args, **kw)
        #print('ansi: ' + str(self.ansi_codes))

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

            # Streams require expanding tabs with 8 spaces
            to_append = msg['content']['text'].expandtabs(8)
            #print(msg)
            self.signaller.emit_signal(TextSignal(to_append, self.ansi_codes))
