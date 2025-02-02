import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import defaultdict

np.random.seed(77)
N=78
K=1
L=210
E=7
R=np.array(range(1,256))

board=np.random.choice(R,size=(N,N))
all_blobs=set()
blobs=defaultdict(list)

fig, ax = plt.subplots(figsize=(10, 10))
im = ax.imshow(board, cmap='twilight_shifted_r', interpolation='gaussian')
ax.axis('off')

def one(a):
    global R
    n,m,r=len(a),len(a[0]),defaultdict(list)
    f=lambda i,j,n,m:[[x,y,a[x,y]] for x,y in [(i+K,j),(i-K,j),(i,j+K),(i,j-K),(i+K,j+K),(i-K,j-K),(i+K,j-K),(i-K,j+K)] if 0<=x<n and 0<=y<m]
    
    for i in blobs:
        for j in blobs[i]:
            k=np.random.choice(range(1,E+1))
            t=f(*j,n,m)[:-k]
            for x,y,z in t:
                if (x,y) not in all_blobs:
                    all_blobs.add((x,y))
                    r[i].append((x,y))
                    a[x,y]=i

    for i in r:
        blobs[i].extend(r[i])

    for i in range(n):
        for j in range(m):
            t=f(i,j,n,m)
            x=round(np.mean([k[-1] for k in t]))
            if x>L:
                if (i,j) not in all_blobs:
                    R=np.fromiter([k for k in R if k!=x],dtype='int32')
                    blobs[a[i,j]].append((i,j))
                    all_blobs.add((i,j))
            if (i,j) not in all_blobs:
                a[i,j]=np.random.choice(R)
                
    return a

def up(k):
    global board
    board=one(board)
    im.set_data(board)
    return [im]

anim = FuncAnimation(fig, up, frames=200, interval=200, blit=True)

# anim.save('animation.gif', writer='pillow', fps=5)

plt.show()