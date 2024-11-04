import numpy as np
import matplotlib.pyplot as plt

# x_train = np.random.randint(10,50,size=(30,2))
x_train = np.array([[10, 50], [20, 30], [25, 30], [20, 60], [15, 70], [40, 40], [30, 45], [20, 45], [40, 30], [7, 35]])
# y_train = np.random.choice([1,-1],size=30)
y_train = np.array([-1, 1, 1, -1, -1, 1, 1, -1, 1, -1])


def binary_classications(a,b,N,L,E):
    w=[0,-1]
    f=lambda x:np.sign(x[0]*w[0]+x[1]*w[1])
    last_er_idx=-1
    n=len(a)
    for _ in range(N):
        for i in range(n):
            if b[i]*f(a[i])<0:
                w[0]=w[0]+L*b[i]
                last_er_idx=i
        s=sum(1 for i in range(n) if b[i]*f(a[i])<0)
        if s==0:
            break
    if last_er_idx>-1:
        w[0]=w[0]+E*b[last_er_idx]
    return a,b,w

x_train,y_train,w=binary_classications(x_train,y_train,50,.1,.1)
line_x = list(range(max(x_train[:, 0])))
line_y=[w[0]*x for x in line_x]
x_0,x_1=x_train[y_train==1],x_train[y_train==-1]

plt.scatter(x_0[:,0],x_0[:,1],color='red')
plt.scatter(x_1[:,0],x_1[:,1],color='blue')
plt.plot(line_x,line_y,color='green')

plt.xlim([0,45])
plt.ylim([0,75])
plt.ylabel('length')
plt.xlabel('width')
plt.grid(True)
plt.show()