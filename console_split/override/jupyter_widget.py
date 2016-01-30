from console_split.ui.signal_content import TextSignal, HtmlSignal
from console_split.ui.signaller import Signaller
from console_split.modified_qtconsole.jupyter_widget import JupyterWidget
_JupyterWidgetBase = JupyterWidget

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class JupyterWidget(_JupyterWidgetBase):
    signaller = None

    #---------------------------------------------------------------------------
    # 'object' interface
    #---------------------------------------------------------------------------

    def __init__(self, *args, **kw):
        super(JupyterWidget, self).__init__(*args, **kw)
        self.include_other_output = True
        self.signaller = Signaller()
        #Connect output slot
        self.signaller.connect_signal(self.insert_view)
        #self.set_default_style('linux')
        #self.set_default_style('nocolor')

    #------ Trait change handlers --------------------------------------------

    def _style_sheet_changed(self):
        """ Set the style sheets of the underlying widgets.
        """
        self.setStyleSheet(self.style_sheet)
        if self._control is not None:
            self._control.document().setDefaultStyleSheet(self.style_sheet)
            bg_color = self._control.palette().window().color()
            self._ansi_processor.set_background_color(bg_color)

        if self._page_control is not None:
            self._page_control.document().setDefaultStyleSheet(self.style_sheet)

        if self._view is not None:
            #print('set view style')
            self._view.document().setDefaultStyleSheet(self.style_sheet)


    #---------------------------------------------------------------------------
    # 'BaseFrontendMixin' abstract interface
    #---------------------------------------------------------------------------

    def _handle_execute_result(self, msg):
        """Handle an execute_result message"""
        if self.include_output(msg):
            self.flush_clearoutput()
            content = msg['content']
            prompt_number = content.get('execution_count', 0)
            data = content['data']
            if 'text/plain' in data:
                ###self._append_plain_text(self.output_sep, True)
                to_append = self.output_sep
                self.signaller.emit_signal(TextSignal(to_append))

                ###self._append_html(self._make_out_prompt(prompt_number), True)
                to_append = self._make_out_prompt(prompt_number)
                self.signaller.emit_signal(HtmlSignal(to_append))

                text = data['text/plain']
                # If the repr is multiline, make sure we start on a new line,
                # so that its lines are aligned.
                if "\n" in text and not self.output_sep.endswith("\n"):
                    ###self._append_plain_text('\n', True)
                    to_append = '\n'
                    self.signaller.emit_signal(TextSignal(to_append))

                ###self._append_plain_text(text + self.output_sep2, True)
                to_append = text + self.output_sep2
                # append in command_view
                self.signaller.emit_signal(TextSignal(to_append))
                self.signaller.emit_signal(TextSignal('\n'))

    def _handle_display_data(self, msg):
        """The base handler for the ``display_data`` message."""
        # For now, we don't display data from other frontends, but we
        # eventually will as this allows all frontends to monitor the display
        # data. But we need to figure out how to handle this in the GUI.
        if self.include_output(msg):
            self.flush_clearoutput()
            data = msg['content']['data']
            metadata = msg['content']['metadata']
            # In the regular JupyterWidget, we simply print the plain text
            # representation.
            if 'text/plain' in data:
                text = data['text/plain']
                ###self._append_plain_text(text, True)
                self.signaller.emit_signal(TextSignal(text))
            # This newline seems to be needed for text and html output.
            ###self._append_plain_text(u'\n', True)
            self.signaller.emit_signal(TextSignal(u'\n'))