n,m,r=int(input()),int(input()),[]
for i in range(n):
    t=[]
    for j in range(m):
        t.append(input())
    r.append(' '.join(t))
print(*r,sep='\n')