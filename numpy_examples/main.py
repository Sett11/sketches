import numpy as np

def gen_fib():
    a,b=1,1
    while True:
        yield b
        a,b=b,a+b

g=gen_fib()

a=np.array([next(g) for _ in range(81)])
b=a.reshape(3,3,3,3)
print(b[-1,-1,-1,-1])

a1=np.arange(10)
a1.fill(9)
print(a1)
print(np.empty(10))
print(np.eye(5,5))
print(np.identity(5))
print(np.zeros(10))
print(np.ones(10))
print(np.full(5,5))
print(np.empty((2,2),dtype='int16'))
print(np.mat('1,2;3,4'))
print(np.diag(range(5)))
print(np.diag(np.full(5,5)))
print(np.diagflat(b))
print(np.tri(5))
print(np.arange(1,10,.5))
print(np.linspace(1,5,5))
print(np.geomspace(1,5,5))
print(np.logspace(1,5,5))
print(np.cos(np.arange(1,5,.5)))

def gen_fib2(n):
    a,b=1,1
    while n:
        yield b
        a,b=b,a+b
        n-=1

print(np.fromiter(gen_fib2(10),dtype='int16'))

print(np.fromstring(' '.join(map(str,range(1,10))),dtype='int8',sep=' '))