n,c,v=int(input()),0,0

while n>1:
    if n%2!=0:
        v=1
    n//=2
    c+=1

print(c+v)