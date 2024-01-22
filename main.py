a=[[(i,j) for j in range (1,9)] for i in range(1,9)]
b,c,d,e=int(input())-1,int(input())-1,int(input()),int(input())
q=set()
i,j=b,c
while i>=0 and j>=0:
    q.add(a[i][j])
    i-=1
    j-=1
i,j=b,c
while i<8 and j<8:
    q.add(a[i][j])
    i+=1
    j+=1
i,j=b,c
while i>=0 and j<8:
    q.add(a[i][j])
    i-=1
    j+=1
i,j=b,c
while i<8 and j>=0:
    q.add(a[i][j])
    i+=1
    j-=1
print(['NO','YES'][(d,e) in q])