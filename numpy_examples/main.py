import numpy as np

print(np.r_[1:9,25])

print(np.c_[1:9])

print(np.c_[np.arange(1,4),np.arange(4,7)])

a=np.arange(10)
print(np.hsplit(a,2))
a.shape=-1,1
print(np.vsplit(a,2))

b=np.arange(18)
b.shape=3,3,2
print(b)
print(np.array_split(b,2,axis=2))

a=np.arange(1,15)
b=a[2:4].copy()
b[0]=90
print(a,b)
c=np.array([(1,2,3),(10,20,30),(100,200,300),(4,5,6)])
print(c[:,2])

d=np.arange(1,82)
d.shape=3,3,3,3
print(d[1,2,0,1])
print(d[:,1,2,:],end='\n')
print(d[...,2])

e=np.arange(1,10)
e[[1,2,5]]=2
ee=e[[1,3,7]]
print(e,ee)

j=np.arange(1,20)
print(j[j>8])