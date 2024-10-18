import numpy as np


a=np.ones(5)
print(np.unique(a))
b=np.array([1,2,3,4]*2)
c,d=np.unique(b,return_inverse=True)
print(c[d])
e,j=np.arange(10),np.arange(1,5)
print(np.in1d(e,j))
print(np.intersect1d(e,j))
print(np.union1d(e,j))
print(np.setdiff1d(e,j))
print(np.setdiff1d(j,e))
print(np.setxor1d(j,e))