import numpy as np
import matplotlib.pyplot as plt

x=np.arange(0,10.1,0.1)
y=np.array([a**3-10*a**2+3*a+500 for a in x])
x_train,y_train=x[::2],y[::2]
N=13
L=20

X=np.array([[a**n for n in range(N)] for a in x])
IL=np.array([[L if i==j else 0 for j in range(N)] for i in range(N)])
IL[0][0]=0
X_train=X[::2]
Y=y_train

A=np.linalg.inv(X_train.T@X_train+IL)
w=A@X_train.T@Y

print(w)

yy=[np.dot(w,x) for x in X]
plt.plot(x,yy)
plt.plot(x,y)
plt.grid(True)
plt.show()