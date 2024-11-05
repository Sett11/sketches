import numpy as np
import matplotlib.pyplot as plt

def loss(w,x,y):
    M=np.dot(w,x)*y
    return 2/(1+np.exp(M))

def df(w,x,y):
    L1=1.0
    M=np.dot(w,x)*y
    return -2*(1+np.exp(M))**(-2)*np.exp(M)*x*y+L1*np.sign(w)

x_train = np.array([x+[10*x[0], 10*x[1], 5*(x[0]+x[1])] for x in [[10, 50], [20, 30], [25, 30], [20, 60], [15, 70], [40, 40], [30, 45], [20, 45], [40, 30], [7, 35]]])
y_train = np.array([-1, 1, 1, -1, -1, 1, 1, -1, 1, -1])

fn=len(x_train[0])
n_train=len(x_train)
w=np.zeros(fn)
nt=.00001
lm=.01
N=5000
Q=np.mean([loss(w,x,y) for x,y in zip(x_train,y_train)])
Q_plot=[Q]

for i in range(N):
    k=np.random.randint(0,n_train-1)
    ek=loss(w,x_train[k],y_train[k])
    w=w-nt*df(w,x_train[k],y_train[k])
    Q=lm*ek+(1-lm)*Q
    Q_plot.append(Q)

Q = np.mean([loss(x, w, y) for x, y in zip(x_train, y_train)])
print(w)
print(Q)
plt.plot(Q_plot)
plt.grid(True)
plt.show()