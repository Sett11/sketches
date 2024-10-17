import numpy as np

# def gen_fib():
#     a,b=1,1
#     while True:
#         yield b
#         a,b=b,a+b

# g=gen_fib()

# a=np.array([next(g) for _ in range(81)])
# b=a.reshape(3,3,3,3)
# print(b[-1,-1,-1,-1])

# a1=np.arange(10)
# a1.fill(9)
# print(a1)
# print(np.empty(10))
# print(np.eye(5,5))
# print(np.identity(5))
# print(np.zeros(10))
# print(np.ones(10))
# print(np.full(5,5))
# print(np.empty((2,2),dtype='int16'))
# print(np.mat('1,2;3,4'))
# print(np.diag(range(5)))
# print(np.diag(np.full(5,5)))
# print(np.diagflat(b))
# print(np.tri(5))
# print(np.arange(1,10,.5))
# print(np.linspace(1,5,5))
# print(np.geomspace(1,5,5))
# print(np.logspace(1,5,5))
# print(np.cos(np.arange(1,5,.5)))

# def gen_fib2(n):
#     a,b=1,1
#     while n:
#         yield b
#         a,b=b,a+b
#         n-=1

# print(np.fromiter(gen_fib2(10),dtype='int16'))

# print(np.fromstring(' '.join(map(str,range(1,10))),dtype='int8',sep=' '))



# a=np.ones((3,4,5))

# a.shape=12,5
# # transposition matrix
# print(a.T)

# print(a.reshape(60))

# b=a.reshape(-1,6)

# c=np.zeros((2,5,7))

# print(c.ravel())
# c.shape=-1
# print(c)

# c.resize((2,5,6))

# print(c.size,c.itemsize)

# d=np.array(range(11))
# d.resize(4,5)
# print(d)

# e=np.arange(10)
# e.shape=-1,1
# print(e)

# f=np.arange(32).reshape(8,2,2)
# f=np.expand_dims(f,axis=0)
# f[*[0]*len(f.shape)]=-100
# f=np.append(f,f,axis=0)
# ff=np.delete(f,0,axis=0)
# ff=np.expand_dims(ff,axis=-1)
# print(ff.shape)
# print(ff)
# ff=np.squeeze(ff)
# print(ff)

# aa=np.arange(1,5)
# bb=np.arange(5,9)
# aa.shape=-1,2
# bb.shape=2,-1
# print(aa)
# print(bb)
# print(np.hstack([aa,bb]))
# print(np.vstack([aa,bb]))

# cc=np.arange(1,5)
# cc.shape=-1,2
# dd=np.arange(5,11)
# dd=dd.reshape(-1,3)
# print(np.hstack([cc,dd]))

# ee=np.arange(1,7)
# ee.shape=-1,3
# print(ee)
# jj=np.arange(7,22)
# jj=jj.reshape(-1,3)
# print(np.vstack([ee,jj]))

# x=np.fromiter(range(10),dtype='int16')
# y=np.fromstring(' '.join(map(str,range(10,20))),sep=' ')
# print(np.column_stack([x,y]))
# print(np.row_stack([x,y]))

# x=np.arange(1,13)
# y=np.arange(13,26)
# x.resize(3,3,2)
# y.resize(3,3,2)
# z1=np.concatenate([x,y],axis=0)
# z2=np.concatenate([x,y],axis=1)
# z3=np.concatenate([x,y],axis=2)
# print(z1.shape,z2.shape,z3.shape)

# print(np.r_[1:9,25])

# print(np.c_[1:9])

# print(np.c_[np.arange(1,4),np.arange(4,7)])

# a=np.arange(10)
# print(np.hsplit(a,2))
# a.shape=-1,1
# print(np.vsplit(a,2))

# b=np.arange(18)
# b.shape=3,3,2
# print(b)
# print(np.array_split(b,2,axis=2))