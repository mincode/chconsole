class A:
    def f(self):
        return 'class A'


class B(A):
    def f(self):
        return 'class B'


class C(B):
    def f(self):
        my_super = super(C, self)
        print(my_super)
        return super(B, my_super).f()


c = C()
print(c.f())
