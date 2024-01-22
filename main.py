a,k=[[0]*8 for i in range(1,9)],True
for i in range(8):
    for j in range((0 if k else 1),8,2):
        a[i][j]=1
    k=not k
b,c,d,e=int(input()),int(input()),int(input()),int(input())
print(['NO','YES'][a[b-1][c-1]==a[d-1][e-1]])