from .context_menu import PageNoPasteMenu

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class PlainPageMixin(object):
    def make_context_menu(self, pos):
        return PageNoPasteMenu(self, pos, self.input_target)
