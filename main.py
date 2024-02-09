from string import digits as d, ascii_letters as a
from random import choice,sample
from re import sub
a=sub(r'[lIoO]','',a)
f,n,m=lambda n: ''.join(sample(a,n)[:-1])+choice(d[2:]),int(input()),int(input())
print(*[f(m) for _ in range(n)],sep='\n')