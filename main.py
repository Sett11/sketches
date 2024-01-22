a,b,c,d=int(input()),int(input()),int(input()),int(input())
r=[]
for i in range(a-1,a+2):
    for j in range(b-1,b+2):
        if i>=0 and i<9 and j>=0 and j<9:
            r.append((i,j))
print(['NO','YES'][(c,d) in r])