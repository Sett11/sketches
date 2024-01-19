from sys import stdin
from re import findall

def f(a):
    state='a'
    for i in range(len(a)):
        if not a[i].isdigit():
            return False
        if state=='a':
            if a[i]=='1':
                state='b'
        elif state=='b':
            if a[i]=='1':
                state='a'
            else:
                state='c'
        else:
            if a[i]=='0':
                state='b'
    return state=='a'

for i in stdin:
    j=i.strip()
    if f(findall(r'.',j)):
        print(j)