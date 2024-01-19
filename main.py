from sys import stdin
from re import sub

for i in stdin:
    j=i.strip()
    print(sub(r'human','computer',j))