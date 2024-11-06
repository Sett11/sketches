import numpy as np
import matplotlib.pyplot as plt
from sklearn import tree

x=np.arange(0,np.pi,.1).reshape(-1,1)
y=np.cos(x)

clf=tree.DecisionTreeRegressor(max_depth=3)
clf=clf.fit(x,y)
yy=clf.predict(x)

# tree.plot_tree(clf)
plt.plot(x, y, label="cos(x)")
plt.plot(x, yy, label="DT Regression")
plt.grid()
plt.legend()
plt.title('max_depth=3')
plt.show()