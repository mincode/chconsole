class CMC(type):
    def __init__(self, name, bases, dct):
        print("Creating class %s using CustomMetaclass" % name)
        super(CMC, self).__init__(name, bases, dct)


class A(metaclass=CMC):
    pass


class B:
    def g(self):
        return 'b'

print(A())
print(type(A))
print(type(B))

MA = type(A)
print(MA==CMC)