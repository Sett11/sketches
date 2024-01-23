mx = -10e7
s = 0
for i in range(10):
    x = int(input())
    if x < 0:
        s += x
        if x > mx:
            mx = max(x,mx)
if s:
    print(s,mx,sep='\n')
else:
    print('NO')