from functools import singledispatch

__author__ = 'Manfred Minimair <manfred@minimair.org>'


class S:
    b = True


class T(S):
    c = False


@singledispatch
def f(x):
    raise NotImplementedError

@f.register(str)
def _(x):
    print('This is a string.')


@f.register(S)
def _(x):
    print('This is S')


@f.register(T)
def _(x):
    print('This is T')

f('aa')
s = S()
f(s)
t = T()
f(t)
