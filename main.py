from string import digits as d, ascii_uppercase as a
from random import choice,sample
from re import sub
a=sub(r'[IO]','',a)
f,n,m=lambda n:'a'+''.join(sample(a,n-1)[:-1])+choice(d[2:]),int(input()),int(input())
print(*[f(m) for _ in range(n)],sep='\n')