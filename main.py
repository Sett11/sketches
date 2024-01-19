from sys import stdin
from re import search

for i in stdin:
    j=i.strip()
    if search(r'z(.){3}z',j):
        print(j)