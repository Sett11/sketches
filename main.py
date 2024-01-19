from sys import stdin
from re import sub

for i in stdin:
    print(sub(r'(\w)\1+',lambda x:x.group()[0],i.strip()))