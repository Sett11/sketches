import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier

def get_grid(data):
    x_min,x_max=data[:,0].min(),data[:,0].max()
    y_min,y_max=data[:,1].min(),data[:,1].max()
    return np.meshgrid(np.arange(x_min,x_max,1),np.arange(y_min,y_max,1))

t=[[(85, 174), (93, 156), (103, 176), (113, 152), (123, 133), (128, 160), (147, 127), (152, 137), (180, 124), (180, 148), (205, 133), (207, 113), (199, 158), (222, 168), (235, 137), (237, 152), (265, 149), (258, 180), (237, 196), (255, 214), (270, 203), (280, 186), (280, 228), (269, 239), (300, 203), (289, 240), (279, 270), (294, 271), (308, 238), (118, 187), (154, 154)], [(157, 226), (180, 205), (179, 238), (196, 225), (171, 256), (201, 255), (184, 288), (218, 254), (215, 293), (233, 282), (217, 330), (226, 316), (241, 314), (253, 337), (267, 314), (278, 335), (286, 349), (290, 314), (309, 345), (328, 347), (329, 314), (314, 322), (342, 286), (356, 314), (360, 332), (368, 286), (376, 307), (387, 273), (384, 248), (395, 289), (377, 263), (389, 213), (409, 224), (409, 258), (376, 202), (380, 169), (408, 186), (408, 205), (424, 164), (406, 149), (436, 197), (427, 242), (419, 273), (402, 313), (380, 335)]]
n1=len(t[0])
n2=len(t[1])

train_data=np.r_[t[0],t[1]]
train_labels=np.r_[np.ones(n1)*-1,np.ones(n2)]

XN=len(train_data)
T=1
max_depth=2
w=np.ones(XN)/XN
algs=[]
alfa=[]

for i in range(T):
    algs.append(DecisionTreeClassifier(criterion='gini',max_depth=max_depth))
    algs[i].fit(train_data,train_labels,sample_weight=w)
    predicted=algs[i].predict(train_data)
    N=np.sum(np.abs(train_labels-predicted)/2*w)
    alfa.append( 0.5 * np.log((1 - N) / N) if N != 0 else np.log((1-1e-8) / 1e-8))

    w=w*np.exp(-1*alfa[i]*train_labels*predicted)
    w=w/np.sum(w)

predicted=alfa[0]*algs[0].predict(train_data)
for i in range(1,T):
    predicted+=alfa[i]*algs[i].predict(train_data)

N=np.sum(np.abs(train_labels-np.sign(predicted))/2)

print(f'Nubers error {N} for composition {T} trees')

xx,yy=get_grid(train_data)
predicted=alfa[0]*algs[0].predict(np.c_[xx.ravel(),yy.ravel()]).reshape(xx.shape)
for i in range(1,T):
    predicted+=alfa[i]*algs[i].predict(np.c_[xx.ravel(),yy.ravel()]).reshape(xx.shape)

plt.pcolormesh(xx,yy,predicted,cmap='spring',shading='auto')
plt.scatter(train_data[:, 0], train_data[:, 1], c=train_labels, s=5000 * w, cmap='spring', edgecolors='black', linewidth=1.5)
plt.show()