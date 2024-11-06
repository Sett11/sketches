import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor

x=np.arange(0,np.pi,.1)
n_samles=len(x)
y=np.cos(x)+np.random.normal(.0,.1,n_samles)
x=x.reshape(-1,1)

clf=RandomForestRegressor(max_depth=2,n_estimators=10,random_state=1)
clf.fit(x,y)
yy=clf.predict(x)

plt.plot(x, y, label="cos(x)")
plt.plot(x, yy, label="DT Regression")
plt.grid()
plt.legend()
plt.title('Four trees in depth two')
plt.show()