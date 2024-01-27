from string import ascii_lowercase as a,ascii_uppercase as b
from re import sub

s=input().split()
f=lambda s,l: ''.join([a[(a.index(i)+l)%26] if i in a else b[(b.index(i)+l)%26] if i in b else i for i in s])

print(' '.join(f(i,len(sub(r'[^A-z]','',i))) for i in s))