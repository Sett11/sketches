import numpy as np
import matplotlib.pyplot as plt

np.random.seed(1)

r1=.7
D1=1.0
mean1=[0,-3]
V1=[[D1,D1*r1],[D1*r1,D1]]

r2=.7
D2=1.0
mean2=[0,3]
V2=[[D2,D2*r2],[D2*r2,D2]]

N=1000
x1=np.random.multivariate_normal(mean1,V1,N).T
x2=np.random.multivariate_normal(mean2,V2,N).T

mm1=np.mean(x1.T,axis=0)
mm2=np.mean(x2.T,axis=0)

a=(x1.T-mm1).T

VV1 = np.array([[np.dot(a[0], a[0]) / N, np.dot(a[0], a[1]) / N],
                [np.dot(a[1], a[0]) / N, np.dot(a[1], a[1]) / N]])

a = (x2.T - mm2).T
VV2 = np.array([[np.dot(a[0], a[0]) / N, np.dot(a[0], a[1]) / N],
                [np.dot(a[1], a[0]) / N, np.dot(a[1], a[1]) / N]])

Py1,L1=.5,1
Py2,L2=1-Py1,1

b = lambda x, v, m, l, py: np.log(l * py) - 0.5 * (x - m) @ np.linalg.inv(v) @ (x - m).T - 0.5 * np.log(
    np.linalg.det(v))

x=np.array([0,-4])

a=np.argmax([b(x, VV1, mm1, L1, Py1), b(x, VV2, mm2, L2, Py2)])

print(a)

plt.figure(figsize=(7,5))
plt.title(f'Correlation: r1= {r1}, r2 = {r2}')
plt.scatter(x1[0],x1[1],s=10)
plt.scatter(x2[0],x2[1],s=10)
plt.show()