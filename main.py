from functools import reduce
from operator import mul

n=int(input())
a=list(map(int,str(n)))
print(f"Сумма цифр = {sum(a)}",f"Произведение цифр = {reduce(mul,a)}",sep='\n')