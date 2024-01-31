n,m,r,q=int(input()),int(input()),[],[]
for i in range(n):
    t=[]
    for j in range(m):
        t.append(input())
    r.append(' '.join(t))
    q.append(t)
print(*r,sep='\n')
print('')
print(*list(map(lambda x:' '.join(x),zip(*q))),sep='\n')