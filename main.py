import os

r=[]

for i,_,k in os.walk('.'):
    if any(p.endswith('.py') for p in k):
        r.append(i[2:])

with open('solve.txt','w') as w:
    for i in sorted(r):
        w.write(i+'\n')