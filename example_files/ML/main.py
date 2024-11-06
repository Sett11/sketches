import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor

np.random.seed(123)

x=np.arange(0,np.pi/2,.1).reshape(-1,1)
y=np.sin(x)+np.random.normal(0,.1,x.shape)

T=5
max_depth=2
algs=[]
s=np.array(y.ravel())


for i in range(T):
    algs.append(DecisionTreeRegressor(max_depth=max_depth))
    algs[-1].fit(x,s)
    s-=algs[-1].predict(x)


yy=algs[0].predict(x)

for i in range(1,T):
    yy+=algs[i].predict(x)

plt.plot(x,y)
plt.plot(x,yy)
plt.plot(x,s)
plt.grid()
plt.show()