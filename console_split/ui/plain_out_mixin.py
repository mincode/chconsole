from .context_menu import OutMenu

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class PlainOutMixin(object):
    def make_context_menu(self, pos):
        return OutMenu(self, pos, self.input_target)