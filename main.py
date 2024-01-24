n,r=int(input()),[[str(1)]]

while len(r)!=n:
    x,t=int(r[-1][-1])+1,[]
    for i in range(x,x+len(r[-1])+1):
        t.append(str(i))
    r.append(t)

print(*[' '.join(i) for i in r],sep='\n')