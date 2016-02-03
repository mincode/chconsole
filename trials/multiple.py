__author__ = 'Manfred Minimair <manfred@minimair.org>'


class A(object):
    def __init__(self):
        print("A")

    def f(self):
        print("A.f")


class B(object):
    def __init__(self):
        print("B")

    def f(self):
        print("B.f")


class C(B, A):
    def __init__(self):
        A.__init__(self)
        super(C, self).__init__()


c = C()
c.f()
