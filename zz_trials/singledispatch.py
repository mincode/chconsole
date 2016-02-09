from functools import singledispatch

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class A:
    @singledispatch
    def f(self, x):
        raise NotImplementedError

    @f.register(str)
    def f(self, x):
        print('This is a string.')

a = A()
a.f('aa')
