n=int(input())
r=[[0]*n for _ in range(n)]

for i in range(n):
    for j in range(n):
        if i>j:
            k,h=i,j
            while k<n and h>=0:
                r[k][h]=r[k-1][h]+1
                k+=1
                h-=1
        if i<j:
            k,h=i,j
            while k>=0 and h<n:
                r[k][h]=r[k][h-1]+1
                k-=1
                h+=1
for i in range(n):
    r[i][i]=0
    print(*r[i])