from sys import stdin
from re import sub

def f(s):
    return f'{s[1]}{s[0]}{s[2:]}' if len(s)>1 else s

for i in stdin:
    print(sub(r'\b(\w)+\b',lambda x:f(x.group()),i.strip()))