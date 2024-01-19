from sys import stdin
from re import sub,IGNORECASE

for i in stdin:
    j=i.strip()
    print(sub(r'\b(a)+\b','argh',j,count=1,flags=IGNORECASE))