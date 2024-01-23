from functools import reduce
from operator import mul

print(reduce(mul,map(int,input())))