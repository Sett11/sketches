import numpy as np
from time import time


a=np.arange(1,11)
print(np.sum(a))
print(a.sum())
print(np.min(a))
print(a.min())
print(np.max(a))
print(a.max())
print(np.mean(a))
print(a.mean())
print(np.median(a))
print(np.quantile(a,.25))
print(np.quantile(a,.50))
print(np.quantile(a,.75))

b=np.arange(1,10)
b.resize(3,2)
print(b.sum())
print(b.sum(axis=1))
print(b.sum(axis=0))
print(np.amax(a))
print(np.argmax(a))
print(np.argmin(a))

print(np.random.rand(5))
print(np.random.rand(3,3,3))
print(np.random.randint(5,10,size=(2,2,2)))
print(np.random.randn(3))
print(np.random.pareto(3,size=(2,2)))
print(np.random.beta(3,7,size=(2,2)))
np.random.seed(13)
c=np.random.permutation(10)
print(np.var(c))
print(np.std(c))

def f(v=True):
    if v:
        return sum(range(1,20000000))
    return np.sum(np.arange(1,20000000))

s=time()
print(f(False),time()-s)