from datetime import datetime
import time
from decimal import Decimal
from math import pi

class Temporal_number:

    def __init__(self,number):
        self.__n=number
    
    def _get_fenomenal_part(self):
        return self.__n/(datetime.now().timestamp()/1000)
    
    @property
    def number(self):
        return self.__n+self._get_fenomenal_part()
    
    def __str__(self):
        return str(self.number)
    
    def __eq__(self,other):
        return self.number==other.number
    
    def __lt__(self,other):
        return self.number<=other.number
    
    def __le__(self,other):
        return self.number<other.number
    
    def __gt__(self,other):
        return self.number>=other.number
    
    def __ge__(self,other):
        return self.number>other.number

    def __add__(self,other):
        return Temporal_number(self.number+other.number)
    
    def __mul__(self,other):
        return Temporal_number(self.number*other.number)
    
    def __sub__(self,other):
        return Temporal_number(self.number-other.number)
    
    def __truediv__(self,other):
        return Temporal_number(self.number/other.number)
    
    def __floordiv__(self,other):
        return Temporal_number(self.number//other.number)


def factorial(n,k):
    return k if n<=k else n*factorial(n-k,k)

def fibonacci(n,one,two):
    return one if n<=one else fibonacci(n-one,one,two)+fibonacci(n-two,one,two)

def get_pi():
    time.sleep(1)
    return Temporal_number(pi)

print([Decimal(factorial(Temporal_number(i),Temporal_number(1)).number-factorial(i,1)) for i in range(1,10)])

print([Decimal(fibonacci(Temporal_number(i),Temporal_number(1),Temporal_number(2)).number) for i in range(10)])

print([Decimal(get_pi().number) for _ in range(10)])