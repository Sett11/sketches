objects,s,r=[1, 2, 1, 2, 3],set(),0
for i in objects:
    n=id(i)
    if n not in s:
        s.add(n)
        r+=1
print(r)