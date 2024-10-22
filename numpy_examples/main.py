from sympy import symbols,diff,sin,tan,atan
import numpy as np
from scipy.misc import derivative
import matplotlib.pyplot as plt


x,y=symbols('x y')
print(diff((3*x-1)/(2*x+5)))

a=np.logspace(1,10,30)
b=np.diff(a)
plt.plot(list(a),[0]+list(b))
plt.show()

def f(x):
    return x**2+x**3

print(derivative(f,1.0,dx=1e-3))