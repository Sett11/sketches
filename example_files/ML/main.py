import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm

x_train = [[10, 50], [20, 30], [25, 30], [20, 60], [15, 70], [40, 40], [30, 45], [20, 45], [40, 30], [7, 35]]
x_train = [x + [1] for x in x_train]
y_train = [-1, 1, 1, -1, -1, 1, 1, -1, 1, -1]

clf=svm.SVC(kernel='linear')
clf.fit(x_train,y_train)

line_clf=svm.LinearSVC()
line_clf.fit(x_train,y_train)

v=clf.support_vectors_
w=line_clf.coef_[0]

print(w,v,sep='\n')

x_train=np.array(x_train)
y_train=np.array(y_train)
line_x=list(range(max(x_train[:,0])))
line_y=[-x*w[0]/w[1] - w[2] for x in line_x]

x_0=x_train[y_train==1]
x_1=x_train[y_train==-1]

plt.scatter(x_0[:, 0], x_0[:, 1], color='red')
plt.scatter(x_1[:, 0], x_1[:, 1], color='blue')
plt.scatter(v[:, 0], v[:, 1], s=70, edgecolor=None, linewidths=0, marker='s')
plt.plot(line_x, line_y, color='green')

plt.xlim([0, 45])
plt.ylim([0, 75])
plt.ylabel("length")
plt.xlabel("width")
plt.grid(True)
plt.show()