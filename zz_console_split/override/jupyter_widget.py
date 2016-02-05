from zz_console_split.ui.signal_content import TextSignal, HtmlSignal
from zz_console_split.modified_qtconsole.jupyter_widget import JupyterWidget
_JupyterWidgetBase = JupyterWidget

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class JupyterWidget(_JupyterWidgetBase):
    #---------------------------------------------------------------------------
    # 'object' interface
    #---------------------------------------------------------------------------

    def __init__(self, *args, **kw):
        super(JupyterWidget, self).__init__(*args, **kw)
        self.include_other_output = True
        #self.signaller = Signaller(self.ansi_codes)
        #Connect output slot
        #self.signaller.connect_signal(self.insert_view)
        #self.set_default_style('linux')
        #self.set_default_style('nocolor')
        #print('init overridden JupyterWidget')

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
        #print('execute result')
        #print(msg)
        if self.include_output(msg):
            self.flush_clearoutput()
            content = msg['content']
            prompt_number = content.get('execution_count', 0)
            data = content['data']
            if 'text/plain' in data:
                ###self._append_plain_text(self.output_sep, True)
                to_append = self.output_sep
                self.signaller.emit_signal(TextSignal(to_append, self.ansi_codes))

                ###self._append_html(self._make_out_prompt(prompt_number), True)
                to_append = self._make_out_prompt(prompt_number)
                self.signaller.emit_signal(HtmlSignal(to_append, self.ansi_codes))

                text = data['text/plain']
                # If the repr is multiline, make sure we start on a new line,
                # so that its lines are aligned.
                if "\n" in text and not self.output_sep.endswith("\n"):
                    ###self._append_plain_text('\n', True)
                    to_append = '\n'
                    self.signaller.emit_signal(TextSignal(to_append, self.ansi_codes))

                ###self._append_plain_text(text + self.output_sep2, True)
                to_append = text + self.output_sep2
                # append in command_view
                self.signaller.emit_signal(TextSignal(to_append, self.ansi_codes))
                self.signaller.emit_signal(TextSignal('\n', self.ansi_codes))

    def _handle_display_data(self, msg):
        """The base handler for the ``display_data`` message."""
        # For now, we don't display data from other frontends, but we
        # eventually will as this allows all frontends to monitor the display
        # data. But we need to figure out how to handle this in the GUI.
        #print('display data')
        if self.include_output(msg):
            self.flush_clearoutput()
            data = msg['content']['data']
            metadata = msg['content']['metadata']
            # In the regular JupyterWidget, we simply print the plain text
            # representation.
            if 'text/plain' in data:
                text = data['text/plain']
                ###self._append_plain_text(text, True)
                self.signaller.emit_signal(TextSignal(text, self.ansi_codes))
            # This newline seems to be needed for text and html output.
            ###self._append_plain_text(u'\n', True)
            self.signaller.emit_signal(TextSignal(u'\n', self.ansi_codes))

    def _handle_execute_input(self, msg):
        """Handle an execute_input message"""
        self.log.debug("execute_input: %s", msg.get('content', ''))
#        if self.include_output(msg):
#            self._append_custom(self._insert_other_input, msg['content'], before_prompt=True)
        content = msg['content']
        n = content.get('execution_count', 0)
        self.signaller.emit_signal(TextSignal('\n', self.ansi_codes))
        self.signaller.emit_signal(HtmlSignal(self._make_in_prompt(n), self.ansi_codes))
        self.signaller.emit_signal(TextSignal(content['code'], self.ansi_codes))

    # def _insert_other_input(self, cursor, content):
    #     """Insert function for input from other frontends"""
    #     cursor.beginEditBlock()
    #     start = cursor.position()
    #     n = content.get('execution_count', 0)
    #     cursor.insertText('\n')
    #     self._insert_html(cursor, self._make_in_prompt(n))
    #     cursor.insertText(content['code'])
    #     self._highlighter.rehighlightBlock(cursor.block())
    #     cursor.endEditBlock()
