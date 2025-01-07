import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle

N = 20
board = np.random.randint(low=0,high=256,size=(N, N))
fig, ax = plt.subplots()
im = ax.imshow(board, cmap='plasma', interpolation='nearest')
ax.axis('off')

def one_iteration_for_game_of_life(a):
    return np.random.randint(low=0, high=256, size=(N, N))

def create_mask(ax, N):
    for i in range(N):
        for j in range(N):
            rect = Rectangle((j, i), 1, 1, linewidth=0, edgecolor='none', facecolor='none',zorder=2, clip_path=None)
            ax.add_patch(rect)

def up(k):
    global board
    board = one_iteration_for_game_of_life(board)
    im.set_data(board)
    return [im]

create_mask(ax, N)
anim = FuncAnimation(fig, up, frames=200, interval=200, blit=True)
plt.show()