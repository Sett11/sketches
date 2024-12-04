import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
np.random.seed(42)

N=100
K=1

def one_iteration_for_game_of_life(a):
    n,m,r=len(a),len(a[0]),[]
    for i in range(n):
        for j in range(m):
            t=[a[x,y] for x,y in [(i+K,j),(i-K,j),(i,j+K),(i,j-K),(i+K,j+K),(i-K,j-K),(i+K,j-K),(i-K,j+K)] if 0<=x<n and 0<=y<m and a[x,y]]
            if a[i,j] and len(t) not in [2,3]:
                r.append((i,j,0))
            if not a[i,j] and len(t)==3:
                r.append((i,j,1))
    for i,j,k in r:
        a[i,j]=k
    return a

board=np.random.choice([0,1],size=(N,N))
fig,ax=plt.subplots()
im=ax.imshow(board,cmap='plasma_r',interpolation='bilinear')
ax.axis('off')


def up(_):
    global board,memo
    board=one_iteration_for_game_of_life(board)
    im.set_data(board)
    return [im]

anim=FuncAnimation(fig,up,frames=200,interval=200,blit=True)
plt.show()
# anim.save('game_of_life.gif', writer='imagemagick', fps=10)