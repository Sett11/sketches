from sys import stdin
from re import findall

for i in stdin:
    j=i.strip()
    if len(findall(r'cat',j))>1:
        print(j)