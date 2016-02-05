__author__ = 'Manfred Minimair <manfred@minimair.org>'


class S:
    def pr(self):
        print('This is S')


def template_class(T):
    class A(T):
        def __init__(self):
            T.__init__(self)
    return A


B = template_class(S)
print(type(B))
b = B()
print(b)
b.pr()