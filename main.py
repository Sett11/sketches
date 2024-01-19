from sys import stdin
from re import search

for i in stdin:
    j=i.strip()
    if search(r'\b(\w+)\1\b',j):
        print(j)