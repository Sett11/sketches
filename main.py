l,n,r,s='abcdefgh','12345678',[['.']*8 for _ in range(8)],input()
a,b=7-n.index(s[1]),l.index(s[0])
r[a]=['*']*8
for  i in range(8):
    r[i][b]='*'
i,j=a,b
while i>=0 and j>=0:
    r[i][j]='*'
    i-=1
    j-=1
i,j=a,b
while i<8 and j<8:
    r[i][j]='*'
    i+=1
    j+=1
i,j=a,b
while i<8 and j>=0:
    r[i][j]='*'
    i+=1
    j-=1
i,j=a,b
while i>=0 and j<8:
    r[i][j]='*'
    i-=1
    j+=1
r[a][b]='Q'
for i in [p for p in r]:
    print(*i)