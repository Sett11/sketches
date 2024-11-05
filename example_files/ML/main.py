import numpy as np

S=1000
np.random.seed(123)
x,y=np.random.normal(size=S),np.random.normal(size=S)
z=(x+y)/2

F=np.vstack([x,y,z])
FF=1/S*F@F.T # calculate Gram matrix
L,W=np.linalg.eig(FF) # Calculation of eigenvectors and eigenvalues
WW=np.array([i[1] for i in sorted(zip(L,W.T),key=lambda x:x[0],reverse=True)])

print(sorted(L,reverse=True))