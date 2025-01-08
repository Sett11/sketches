import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import defaultdict
np.random.seed(9)

N,K,life_check=70,1,210
board=np.random.randint(low=0,high=256,size=(N,N))
blobs=defaultdict(list)

fig,ax=plt.subplots()
im=ax.imshow(board,cmap='twilight_shifted_r',interpolation='gaussian')
ax.axis('off')

def one(a):
    n,m,r,b,v,w=len(a),len(a[0]),{},sum(list(blobs.values()),[]),[],{}

    for i in range(n):
        for j in range(m):
            t=[[x,y,a[x,y]] for x,y in [(i+K,j),(i-K,j),(i,j+K),(i,j-K),(i+K,j+K),(i-K,j-K),(i+K,j-K),(i-K,j+K)] if 0<=x<n and 0<=y<m]
            x=round(np.mean([k[-1] for k in t]))
            if (i,j) in b:
                for k in blobs:
                    if k not in v:
                        if (i,j) in blobs[k]:
                            v.append(k)
                            w[k]=t[np.random.choice(range(len(t)))][:-1]
                            break
            if x>life_check:
                r[(i,j)]=x
    for k in w:
        a[*w[k]]=k
        b.append(tuple(w[k]))

    for i in range(n):
        for j in range(m):
            if (i,j) in r:
                if (i,j) in b:
                    if r[(i,j)]>a[i,j]:
                        a[i,j]=r[(i,j)]
                        blobs[a[i,j]].append((i,j))
                else:
                    a[i,j]=r[(i,j)]
                    if a[i,j] not in blobs:
                        blobs[a[i,j]].append((i,j))
            else:
                a[i,j]=np.random.randint(low=0,high=256)

    return a


def up(k):
    global board
    board=one(board)
    im.set_data(board)
    return [im]

anim=FuncAnimation(fig,up,frames=200,interval=200,blit=True)
plt.show()
print(blobs)

# anim.save('game_of_life.gif', writer='imagemagick', fps=10)