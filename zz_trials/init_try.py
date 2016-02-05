__author__ = 'Manfred Minimair <manfred@minimair.org>'


class A:
    def __init__(self, text='', parent=None):
        print(text)
        print(parent)
        pass


class B(A):
    def __init__(self, *args):
        super().__init__(*args)


b = B('text', 'parent')
