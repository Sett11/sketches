a,n=[[1],[1,1],[1,2,1]],int(input())
for i in range(n-2):
    k,t=a[-1],[1]
    for j in range(1,len(k)):
        t.append(k[j]+k[j-1])
    a.append(t+[1])
print(a[n])