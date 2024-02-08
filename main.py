d,r={},[]
for i in input().split():
    r.append(d.get(i,0)+1)
    d[i]=1 if i not in d else d[i]+1
print(*r)