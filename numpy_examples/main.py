import numpy as np
from time import time


a=np.arange(1,10)
a.resize(3,3)
b=np.arange(10,19)
b.resize(3,3)
print(np.dot(a,b))
print(np.matmul(a,b))
print(a@b)
c,d=np.arange(1,10),np.ones(9)
print(np.inner(c,d))
print(np.outer(c,d))

x=np.arange(1,4)
y=x**2
z=x**3
k=np.array([x,y,z])
print(np.linalg.solve(k,np.array([10,20,30])))
kk=np.linalg.inv(k)
print(kk)
print(kk@np.array([10,20,30]))