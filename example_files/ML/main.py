import numpy as np
import matplotlib.pyplot as plt
import time

x=[(98, 62), (80, 95), (71, 130), (89, 164), (137, 115), (107, 155), (109, 105), (174, 62), (183, 115), (164, 153),
     (142, 174), (140, 80), (308, 123), (229, 171), (195, 237), (180, 298), (179, 340), (251, 262), (300, 176),
     (346, 178), (311, 237), (291, 283), (254, 340), (215, 308), (239, 223), (281, 207), (283, 156)]

M=np.mean(x,axis=0)
D=np.var(x,axis=0)
K=3
COLORS=('green', 'blue', 'brown', 'black')

ma=[np.random.normal(M,np.sqrt(D/10),2) for _ in range(K)]
ro=lambda x,y:np.mean((x-y)**2)

plt.ion()
n=0
while n<10:
    X=[[] for _ in range(K)]
    for i in x:
        r=[ro(i,j) for j in ma]
        X[np.argmin(r)].append(i)
    ma=[np.mean(xx,axis=0) for xx in X]

    plt.clf()
    for i in range(K):
        xx = np.array(X[i]).T
        plt.scatter(xx[0], xx[1], s=10, color=COLORS[i])

    mx = [m[0] for m in ma]
    my = [m[1] for m in ma]
    plt.scatter(mx, my, s=50, color='red')

    plt.draw()
    plt.gcf().canvas.flush_events()
    # plt.savefig(f"lloyd {n+1}.png")
    time.sleep(0.2)
    n+=1

plt.ioff()

for i in range(K):
    xx=np.array(X[i]).T
    plt.scatter(xx[0],xx[1],s=10,color=COLORS[i])

mx=[i[0] for i in ma]
my=[i[1] for i in ma]
plt.scatter(mx,my,s=50,color='red')
plt.show()