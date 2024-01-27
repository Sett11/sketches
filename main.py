from math import pi

def f(r):
    return 2*pi*r,pi*r**2

print(*f(float(input())))