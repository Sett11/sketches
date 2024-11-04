import numpy as np
import matplotlib.pyplot as plt

def loss(w,x,y):
    M=np.dot(w,x)*y
    return 2/(1+np.exp(M))

def df(w,x,y):
    M=np.dot(w,x)*y
    return -2*(1+np.exp(M))**(-2)*np.exp(M)*x*y

x_train = np.array([i+[1] for i in [[10, 50], [20, 30], [25, 30], [20, 60], [15, 70], [40, 40], [30, 45], [20, 45], [40, 30], [7, 35]]])
y_train = np.array([-1, 1, 1, -1, -1, 1, 1, -1, 1, -1])

n_train=len(x_train)
w=np.zeros(3)
nt=.0005
lm=.01
N=500
Q=np.mean([loss(w,x,y) for x,y in zip(x_train,y_train)])
Q_plot=[Q]

for i in range(N):
    k=np.random.randint(0,n_train-1)
    ek=loss(w,x_train[k],y_train[k])
    w=w-nt*df(w,x_train[k],y_train[k])
    Q=lm*ek+(1-lm)*Q
    Q_plot.append(Q)

print(w)


line_x=list(range(max(x_train[:,0])))
line_y=[-x*w[0]/w[1]-w[2]/w[1] for x in line_x]

x_0=x_train[y_train==1]
x_1=x_train[y_train==-1]

plt.scatter(x_0[:,0],x_0[:,1],color='red')
plt.scatter(x_1[:,0],x_1[:,1],color='blue')
plt.plot(line_x,line_y,color='green')

plt.xlim([0,45])
plt.ylim([0,75])
plt.ylabel('length')
plt.xlabel('width')
plt.grid(True)
plt.show()