d,r={},''
for i in input().split():
    if i in d:
        r+=f'{i}_{d[i]} '
        d[i]+=1
    else:
        d[i]=1
        r+=i+' '
print(r)