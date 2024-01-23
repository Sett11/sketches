n,c=int(input()),0
d=[25,10,5,1]
for i in d:
    a,b=divmod(n,i)
    c+=a
    n=b
print(c)