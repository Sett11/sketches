b=[['.']*8 for _ in range(8)]
k,h=input()
j,i='abcdefgh'.index(k),7-'12345678'.index(h)
b[i][j]='N'
for x,y in [[i+1,j+2],[i+2,j+1],[i+1,j-2],[i+2,j-1],[i-1,j-2],[i-2,j-1],[i-1,j+2],[i-2,j+1]]:
    if 0<=x<8 and 0<=y<8:
        b[x][y]='*'
for w in b:
    print(*w)