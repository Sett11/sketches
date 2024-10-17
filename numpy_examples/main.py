import numpy as np
from time import time


a=np.arange(1,15)
b=np.arange(2,16)
print(a>5)
print(np.greater(a,b))
print(a!=8)
print(np.less(a,b))
print(a==8)
print(np.equal(a,b))
print(np.not_equal(a,b))
if np.array_equal(a,b):
    print(9)
if not np.array_equal(a,b):
    print(8)

print(np.any(a>5))
print(np.all(a>0))

c=np.array([2,3,np.nan,np.inf])
print(np.isinf(c))
print(np.isnan(c))
print(c[~np.isnan(c)])
print(c[~np.isinf(c)])
print(c[np.isfinite(c)])
d=np.array([1.-4.j,2.+5.j-5,3.+0.j])
print(np.iscomplex(d))
print(np.isreal(d))

e=np.array([True,False,True,False])
j=np.array([True]*2+[False]*2)
print(np.logical_and(e,j))
print(np.logical_not(e))
print(np.logical_or(e,j))
print(np.logical_xor(e,j))