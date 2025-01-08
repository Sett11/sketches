import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

N,K,life_check=50,1,210
board=np.random.randint(low=0,high=256,size=(N,N))
blobs={}

fig,ax=plt.subplots()
im=ax.imshow(board,cmap='twilight_shifted_r',interpolation='nearest')
ax.axis('off')

def one(a):
    # return np.random.randint(low=0,high=256,size=(N,N))
    n,m,r,b=len(a),len(a[0]),{},{}

    for i in range(n):
        for j in range(m):
            t=[[x,y,a[x,y]] for x,y in [(i+K,j),(i-K,j),(i,j+K),(i,j-K),(i+K,j+K),(i-K,j-K),(i+K,j-K),(i-K,j+K)] if 0<=x<n and 0<=y<m]
            x=round(np.mean([k[-1] for k in t]))
            for v in blobs:
                if (i,j) in v:
                    ...
            if x>life_check:
                r[(i,j)]=x

    for i in range(n):
        for j in range(m):
            a[i,j]=np.random.randint(low=0,high=256)

    return a

def up(k):
    global board
    board=one(board)
    im.set_data(board)
    return [im]

anim=FuncAnimation(fig,up,frames=200,interval=200,blit=True)
plt.show()

# anim.save('game_of_life.gif', writer='imagemagick', fps=10)