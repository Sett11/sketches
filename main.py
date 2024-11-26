from math import factorial as f
from functools import reduce
from operator import mul
from collections import Counter
from itertools import product
from gmpy2 import is_prime

class Universe_item:
    def __init__(self,number):
        self.number=number
        self.history={'previous_numbers':[],'previous_operation':'','this_number':self.number}

    def __add__(self,other):
        new_number=generate_universe_items(self.number+other.number)
        if isinstance(new_number,str):
            return new_number
        new_number.history['previous_numbers']=[self.number,other.number]
        new_number.history['previous_operation']='+'
        new_number.history['this_number']=new_number.number
        return new_number
    
    def __sub__(self,other):
        new_number=generate_universe_items(self.number-other.number)
        if isinstance(new_number,str):
            return new_number
        new_number.history['previous_numbers']=[self.number,other.number]
        new_number.history['previous_operation']='-'
        new_number.history['this_number']=new_number.number
        return new_number
    
    def __mul__(self,other):
        new_number=generate_universe_items(self.number*other.number)
        if isinstance(new_number,str):
            return new_number
        new_number.history['previous_numbers']=[self.number,other.number]
        new_number.history['previous_operation']='*'
        new_number.history['this_number']=new_number.number
        return new_number
    
    def __truediv__(self,other):
        new_number=generate_universe_items(self.number/other.number)
        if isinstance(new_number,str):
            return new_number
        new_number.history['previous_numbers']=[self.number,other.number]
        new_number.history['previous_operation']='\\'
        new_number.history['this_number']=new_number.number
        return new_number
    
    def __pow__(self,other):
        new_number=generate_universe_items(self.number**other.number)
        if isinstance(new_number,str):
            return new_number
        new_number.history['previous_numbers']=[self.number,other.number]
        new_number.history['previous_operation']='**'
        new_number.history['this_number']=new_number.number
        return new_number

    def __str__(self):
        r=[]
        for i,j in self.__dict__.items():
            r.append(f'{i}: {j}')
        return '\n'.join(r)
    

def generate_universe_items(n):
    if n<1 or n>100:
        return 'This number not exist in my Universe!'

    def pf(n):
        c,r=2,[]
        while c<n*n:
            while n%c==0:
                r.append(c)
                n//=c
            c+=1
        return r
    
    def adn(n):
        return sorted(map(lambda x:reduce(mul,x),product(*[[j**i for i in range(r+1)] for j,r in Counter(pf(n)).items()])))
    
    def fib():
        a=[1,1]
        while a[-1]<100:
            a.append(a[-1]+a[-2])
        return a
    
    def cl(n,r=1):
        return r if n==1 else cl(n//2,r+1) if n%2==0 else cl(n*3+1,r+1)
    
    fib_numbers=fib()
    UI=Universe_item(n)
    UI.collatz_length=cl(n)
    UI.is_even=n%2==0
    UI.is_odd=n%2!=0
    UI.factorial=f(n)
    UI.prime_factors=pf(n)
    UI.all_divisors=adn(n) if n>1 else [1]
    UI.is_perfect=n%sum(UI.all_divisors)==0
    UI.is_fib_number=n in fib_numbers
    UI.sqrt=n**.5
    UI.cbrt=pow(n,1/3)
    UI.sq=n**2
    UI.cb=n**3
    UI.is_prime=is_prime(n)
    return UI

class Universe_numbers:
    def __init__(self):
        self.universe_items=[generate_universe_items(i) for i in range(1,101)]

U=Universe_numbers().universe_items

print(U[10]*U[6])
print(U[70]+U[5])