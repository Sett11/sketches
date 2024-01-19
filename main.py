from sys import stdin
from re import search

for i in stdin:
    j=i.strip()
    if search(r'\bcat\b',j):
        print(j)