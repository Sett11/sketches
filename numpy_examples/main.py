import numpy as np
from time import time


a=np.arange(1,7)
b=np.arange(1,4)
a.resize(2,3)
print(a*b)

c=np.arange(1,19)
c.resize(3,3,2)
d=np.arange(1,7)
d.resize(3,2)
print(c*d)